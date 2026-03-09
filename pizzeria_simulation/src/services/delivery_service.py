"""Delivery service."""
from src.models import PizzeriaState, Order, OrderStatus, OrderType
from src.utils.exceptions import OrderNotFoundError


class DeliveryService:
    """Delivery management service."""

    def __init__(self, state: PizzeriaState):
        self.state = state

    def create_delivery_order(
        self,
        items: list,
        delivery_address: str,
        customer_phone: str,
    ) -> Order:
        from src.services.order_service import OrderService

        order_service = OrderService(self.state)
        return order_service.create_order(
            order_type=OrderType.DELIVERY,
            items=items,
            delivery_address=delivery_address,
            customer_phone=customer_phone,
        )

    def mark_ready_for_delivery(self, order_id: int) -> bool:
        order = next((o for o in self.state.orders if o.id == order_id), None)
        if not order:
            return False

        if order.type != OrderType.DELIVERY:
            return False

        order.status = OrderStatus.OUT_FOR_DELIVERY
        return True

    def mark_delivering(self, order_id: int) -> bool:
        order = next((o for o in self.state.orders if o.id == order_id), None)
        if not order:
            return False

        order.status = OrderStatus.DELIVERING
        return True

    def mark_completed(self, order_id: int) -> bool:
        order = next((o for o in self.state.orders if o.id == order_id), None)
        if not order:
            return False

        order.status = OrderStatus.COMPLETED

        if order.table_id:
            table = next(
                (t for t in self.state.dining_hall.tables if t.id == order.table_id),
                None,
            )
            if table:
                table.is_occupied = False

        return True
