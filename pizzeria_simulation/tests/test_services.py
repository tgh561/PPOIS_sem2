"""Tests for services."""
import pytest
from src.models import create_default_state, OrderType, OrderStatus, OrderItem, PaymentMethod
from src.services import OrderService, SimulationService, AccountingService, DeliveryService
from src.utils.exceptions import OrderNotFoundError


class TestOrderService:
    def test_create_order(self) -> None:
        state = create_default_state()
        service = OrderService(state)

        item = OrderItem(id=1, menu_item_id=1, quantity=1, unit_price=10.0, total_price=10.0)
        order = service.create_order(
            order_type=OrderType.ON_SITE,
            items=[item],
            table_id=1,
        )

        assert order.id == 1
        assert order.type == OrderType.ON_SITE
        assert order.status == OrderStatus.CREATED
        assert state.next_id == 2

    def test_get_order(self) -> None:
        state = create_default_state()
        service = OrderService(state)

        item = OrderItem(id=1, menu_item_id=1, quantity=1, unit_price=10.0, total_price=10.0)
        created_order = service.create_order(
            order_type=OrderType.ON_SITE,
            items=[item],
        )

        order = service.get_order(created_order.id)
        assert order.id == created_order.id

    def test_get_order_not_found(self) -> None:
        state = create_default_state()
        service = OrderService(state)

        with pytest.raises(OrderNotFoundError):
            service.get_order(999)

    def test_change_status(self) -> None:
        state = create_default_state()
        service = OrderService(state)

        item = OrderItem(id=1, menu_item_id=1, quantity=1, unit_price=10.0, total_price=10.0)
        order = service.create_order(
            order_type=OrderType.ON_SITE,
            items=[item],
        )

        service.change_status(order.id, OrderStatus.PAID)
        assert order.status == OrderStatus.PAID

    def test_get_active_orders(self) -> None:
        state = create_default_state()
        service = OrderService(state)

        item = OrderItem(id=1, menu_item_id=1, quantity=1, unit_price=10.0, total_price=10.0)
        order = service.create_order(
            order_type=OrderType.ON_SITE,
            items=[item],
        )

        active = service.get_active_orders()
        assert len(active) == 1
        assert active[0].id == order.id


class TestSimulationService:
    def test_tick(self) -> None:
        state = create_default_state()
        service = SimulationService(state)

        report = service.tick(minutes=10)

        assert report["minutes_passed"] == 10
        assert "moved_to_cooking" in report
        assert "moved_to_baked" in report

    def test_get_kitchen_status(self) -> None:
        state = create_default_state()
        service = SimulationService(state)

        status = service.get_kitchen_status()

        assert "in_queue" in status
        assert "cooking" in status
        assert "baked" in status

    def test_add_to_queue(self) -> None:
        state = create_default_state()
        sim_service = SimulationService(state)
        order_service = OrderService(state)

        item = OrderItem(id=1, menu_item_id=1, quantity=1, unit_price=10.0, total_price=10.0)
        order = order_service.create_order(
            order_type=OrderType.ON_SITE,
            items=[item],
        )

        result = sim_service.add_to_queue(order.id)
        assert result is True
        assert order.id in state.kitchen.orders_in_queue


class TestAccountingService:
    def test_record_payment(self) -> None:
        state = create_default_state()
        service = AccountingService(state)

        payment = service.record_payment(
            order_id=1,
            amount=100.0,
            method=PaymentMethod.CASH,
        )

        assert payment.id == 1
        assert payment.amount == 100.0
        assert payment.method == PaymentMethod.CASH
        assert state.finance.total_revenue == 100.0

    def test_get_payment_history(self) -> None:
        state = create_default_state()
        service = AccountingService(state)

        service.record_payment(order_id=1, amount=100.0, method=PaymentMethod.CASH)
        service.record_payment(order_id=2, amount=200.0, method=PaymentMethod.CARD)

        history = service.get_payment_history()
        assert len(history) == 2

    def test_get_cash_in_register(self) -> None:
        state = create_default_state()
        service = AccountingService(state)

        initial_cash = state.order_desk.cash_register.cash_amount
        service.record_payment(order_id=1, amount=50.0, method=PaymentMethod.CASH)

        assert service.get_cash_in_register() == initial_cash + 50.0


class TestDeliveryService:
    def test_create_delivery_order(self) -> None:
        state = create_default_state()
        service = DeliveryService(state)

        item = OrderItem(id=1, menu_item_id=1, quantity=1, unit_price=10.0, total_price=10.0)
        order = service.create_delivery_order(
            items=[item],
            delivery_address="Pushkina st. 10",
            customer_phone="+375291234567",
        )

        assert order.type == OrderType.DELIVERY
        assert order.delivery_address == "Pushkina st. 10"
        assert order.customer_phone == "+375291234567"

    def test_mark_ready_for_delivery(self) -> None:
        state = create_default_state()
        service = DeliveryService(state)

        item = OrderItem(id=1, menu_item_id=1, quantity=1, unit_price=10.0, total_price=10.0)
        order = service.create_delivery_order(
            items=[item],
            delivery_address="Pushkina st. 10",
            customer_phone="+375291234567",
        )

        result = service.mark_ready_for_delivery(order.id)
        assert result is True
        assert order.status == OrderStatus.OUT_FOR_DELIVERY
