"""Сервис заказов."""
from src.models import PizzeriaState, Order, OrderStatus, OrderType
from src.utils.exceptions import OrderNotFoundError


class OrderService:
    """Сервис для управления заказами."""

    def __init__(self, state: PizzeriaState):
        self.state = state

    def create_order(
        self,
        order_type: OrderType,
        items: list,
        table_id: int | None = None,
        delivery_address: str | None = None,
        customer_phone: str | None = None,
    ) -> Order:
        """Создаёт новый заказ."""
        order = Order(
            id=self.state.next_id,
            type=order_type,
            customer_phone=customer_phone,
            table_id=table_id,
            delivery_address=delivery_address,
            items=items,
            status=OrderStatus.CREATED,
            created_at="2026-03-09T20:30:00",
            estimated_ready_time=None,
            total_price=sum(item.total_price for item in items),
            tips_amount=0.0,
        )
        self.state.next_id += 1
        self.state.orders.append(order)
        return order

    def get_order(self, order_id: int) -> Order:
        """Получает заказ по ID."""
        order = next((o for o in self.state.orders if o.id == order_id), None)
        if not order:
            raise OrderNotFoundError(f"Заказ #{order_id} не найден")
        return order

    def change_status(self, order_id: int, new_status: OrderStatus) -> None:
        """Изменяет статус заказа."""
        order = self.get_order(order_id)
        order.status = new_status

    def get_active_orders(self) -> list[Order]:
        """Получает активные заказы."""
        return [
            o for o in self.state.orders
            if o.status not in (OrderStatus.COMPLETED, OrderStatus.CANCELLED)
        ]

    def cancel_order(self, order_id: int) -> None:
        """Отменяет заказ."""
        order = self.get_order(order_id)
        order.status = OrderStatus.CANCELLED
