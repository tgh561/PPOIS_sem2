"""Tests for models."""
import pytest
from src.models import (
    Order, OrderItem, OrderStatus, OrderType,
    MenuItem, Menu, Payment, PaymentMethod,
    PizzeriaState, create_default_state,
)
from src.enums import EmployeeRole, PizzaBase, ToppingCategory


class TestOrder:
    def test_create_order(self) -> None:
        item = OrderItem(id=1, menu_item_id=1, quantity=2, unit_price=10.0, total_price=20.0)
        order = Order(
            id=1,
            type=OrderType.ON_SITE,
            customer_phone=None,
            table_id=1,
            delivery_address=None,
            items=[item],
            status=OrderStatus.CREATED,
            created_at="2026-03-09T20:00:00",
            estimated_ready_time=None,
            total_price=20.0,
            tips_amount=0.0,
        )

        assert order.id == 1
        assert order.type == OrderType.ON_SITE
        assert order.total_price == 20.0
        assert len(order.items) == 1


class TestOrderType:
    def test_order_type_values(self) -> None:
        assert OrderType.ON_SITE.value == "on_site"
        assert OrderType.DELIVERY.value == "delivery"


class TestOrderStatus:
    def test_order_status_values(self) -> None:
        assert OrderStatus.CREATED.value == "created"
        assert OrderStatus.PAID.value == "paid"
        assert OrderStatus.COMPLETED.value == "completed"
        assert OrderStatus.READY.value == "ready"
        assert OrderStatus.SERVED.value == "served"


class TestPayment:
    def test_create_payment(self) -> None:
        payment = Payment(
            id=1,
            order_id=1,
            amount=100.0,
            method=PaymentMethod.CASH,
            paid_at="2026-03-09T21:00:00",
            success=True,
        )

        assert payment.id == 1
        assert payment.method == PaymentMethod.CASH
        assert payment.amount == 100.0
        assert payment.success is True


class TestPizzeriaState:
    def test_create_default_state(self) -> None:
        state = create_default_state()

        assert state.next_id == 1
        assert state.orders == []
        assert state.payments == []
        assert state.order_desk is not None
        assert state.dining_hall is not None
        assert state.staff_team is not None
        assert state.kitchen is not None
        assert state.finance.total_revenue == 0.0
        assert state.finance.total_tips == 0.0

    def test_default_state_has_menu_items(self) -> None:
        state = create_default_state()
        assert len(state.order_desk.menu.items) > 0

    def test_default_state_has_tables(self) -> None:
        state = create_default_state()
        assert len(state.dining_hall.tables) == 5

    def test_all_tables_free_by_default(self) -> None:
        state = create_default_state()
        occupied = sum(1 for t in state.dining_hall.tables if t.is_occupied)
        assert occupied == 0


class TestMenuItem:
    def test_create_menu_item(self) -> None:
        item = MenuItem(
            id=1,
            name="Pepperoni",
            price=10.0,
            is_available=True,
            category="pizza",
        )

        assert item.id == 1
        assert item.name == "Pepperoni"
        assert item.price == 10.0
        assert item.is_available is True


class TestEmployeeRole:
    def test_employee_role_values(self) -> None:
        assert EmployeeRole.COOK.value == "cook"
        assert EmployeeRole.WAITER.value == "waiter"
        assert EmployeeRole.COURIER.value == "courier"
        assert EmployeeRole.CASHIER.value == "cashier"


class TestPizzaBase:
    def test_pizza_base_values(self) -> None:
        assert PizzaBase.CLASSIC.value == "classic"
        assert PizzaBase.THIN.value == "thin"
        assert PizzaBase.STUFFED.value == "stuffed"
