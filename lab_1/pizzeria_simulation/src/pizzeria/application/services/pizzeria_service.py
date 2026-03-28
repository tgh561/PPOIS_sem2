"""Application service for pizzeria use cases."""
from __future__ import annotations

from pizzeria.domain import CustomerType, OrderStatus, PaymentType, PizzaSize
from pizzeria.domain.exceptions import NotFoundError
from pizzeria.domain.models import Employee, Order, Pizzeria, Table


class PizzeriaService:
    """Facade over Pizzeria aggregate for CLI/use-cases."""

    def __init__(self, pizzeria: Pizzeria):
        self._pizzeria = pizzeria

    @property
    def pizzeria(self) -> Pizzeria:
        """Expose aggregate for read-only access by interface."""
        return self._pizzeria

    def create_dine_in_order(
        self,
        table_number: int,
        guests_count: int,
        pizza_item_ids: list[int],
        size: PizzaSize,
        payment_type: PaymentType,
        drink_item_ids: list[int] | None = None,
    ) -> Order:
        """Create new dine-in order."""
        return self._pizzeria.create_dine_in_order(
            table_number=table_number,
            guests_count=guests_count,
            pizza_item_ids=pizza_item_ids,
            drink_item_ids=drink_item_ids,
            size=size,
            payment_type=payment_type,
        )

    def create_delivery_order(
        self,
        delivery_address: str,
        delivery_phone: str,
        pizza_item_ids: list[int],
        size: PizzaSize,
        payment_type: PaymentType,
        drink_item_ids: list[int] | None = None,
    ) -> Order:
        """Create new delivery order."""
        return self._pizzeria.create_delivery_order(
            delivery_address=delivery_address,
            delivery_phone=delivery_phone,
            pizza_item_ids=pizza_item_ids,
            drink_item_ids=drink_item_ids,
            size=size,
            payment_type=payment_type,
        )

    def confirm_order(self, order_id: int) -> Order:
        """Confirm order."""
        return self._pizzeria.confirm_order(order_id)

    def send_order_to_kitchen(self, order_id: int) -> Order:
        """Send order to kitchen."""
        return self._pizzeria.send_order_to_kitchen(order_id)

    def tick_kitchen(self, minutes: int = 10) -> list[int]:
        """Advance kitchen simulation."""
        return self._pizzeria.tick_kitchen(minutes=minutes)

    def start_delivery(self, order_id: int) -> Order:
        """Start delivery for an order."""
        return self._pizzeria.start_delivery(order_id)

    def tick_delivery(self, minutes: int = 10) -> list[int]:
        """Advance delivery simulation."""
        return self._pizzeria.tick_delivery(minutes=minutes)

    def pay_order(self, order_id: int) -> Order:
        """Process order payment."""
        return self._pizzeria.pay_order(order_id=order_id)

    def complete_order(self, order_id: int) -> Order:
        """Complete order."""
        return self._pizzeria.complete_order(order_id)

    def cancel_order(self, order_id: int) -> Order:
        """Cancel order."""
        return self._pizzeria.cancel_order(order_id)

    def list_orders(self) -> list[Order]:
        """Return all orders sorted by id."""
        return sorted(self._pizzeria.orders, key=lambda order: order.id)

    def list_active_orders(self) -> list[Order]:
        """Return active orders except completed/canceled."""
        return [
            order
            for order in self.list_orders()
            if order.status not in (OrderStatus.COMPLETED, OrderStatus.CANCELED)
        ]

    def get_orders_by_status(self, status: OrderStatus) -> list[Order]:
        """Get orders by status."""
        return [order for order in self._pizzeria.orders if order.status == status]

    def list_orders_for_confirmation(self) -> list[Order]:
        """Orders that can be confirmed."""
        return self.get_orders_by_status(OrderStatus.CREATED)

    def list_orders_for_kitchen(self) -> list[Order]:
        """Orders that can be sent to kitchen."""
        return [
            order
            for order in self.list_orders()
            if order.status in (OrderStatus.CREATED, OrderStatus.CONFIRMED)
        ]

    def list_orders_in_kitchen(self) -> list[Order]:
        """Orders currently being prepared or baked."""
        return [
            order
            for order in self.list_orders()
            if order.status in (OrderStatus.PREPARING, OrderStatus.BAKING)
        ]

    def list_ready_orders(self) -> list[Order]:
        """Orders in READY status."""
        return self.get_orders_by_status(OrderStatus.READY)

    def list_ready_and_completed_orders(self) -> list[Order]:
        """Orders that are ready to hand off or already completed."""
        return [
            order
            for order in self.list_orders()
            if order.status in (OrderStatus.READY, OrderStatus.COMPLETED)
        ]

    def list_ready_for_delivery(self) -> list[Order]:
        """Delivery orders ready to be dispatched."""
        return [
            order
            for order in self.list_orders()
            if order.customer_type == CustomerType.DELIVERY and order.status == OrderStatus.READY
        ]

    def list_active_deliveries(self) -> list[tuple[Order, int]]:
        """Return active delivery tasks with remaining minutes."""
        active: list[tuple[Order, int]] = []
        orders_by_id = {order.id: order for order in self._pizzeria.orders}
        for task in self._pizzeria.delivery.tasks.values():
            order = orders_by_id.get(task.order_id)
            if order is None:
                continue
            active.append((order, task.remaining_minutes))
        return sorted(active, key=lambda item: item[0].id)

    def list_arrived_delivery_unpaid(self) -> list[Order]:
        """Delivery orders arrived to client and waiting for payment."""
        return [
            order
            for order in self.list_orders()
            if order.customer_type == CustomerType.DELIVERY
            and order.status == OrderStatus.OUT_FOR_DELIVERY
            and not order.is_paid
            and not self._pizzeria.delivery.is_in_progress(order.id)
        ]

    def list_orders_for_payment(self) -> list[Order]:
        """Orders eligible for payment right now."""
        return [
            order
            for order in self.list_orders()
            if not order.is_paid
            and (
                (order.customer_type == CustomerType.DINE_IN and order.status == OrderStatus.READY)
                or (
                    order.customer_type == CustomerType.DELIVERY
                    and order.status == OrderStatus.OUT_FOR_DELIVERY
                    and not self._pizzeria.delivery.is_in_progress(order.id)
                )
            )
        ]

    def list_orders_for_completion(self) -> list[Order]:
        """Orders eligible for completion right now."""
        return [
            order
            for order in self.list_orders()
            if order.is_paid
            and (
                (order.customer_type == CustomerType.DINE_IN and order.status == OrderStatus.READY)
                or (
                    order.customer_type == CustomerType.DELIVERY
                    and order.status == OrderStatus.OUT_FOR_DELIVERY
                    and not self._pizzeria.delivery.is_in_progress(order.id)
                )
            )
        ]

    def list_free_tables(self) -> list[Table]:
        """Return all currently free tables."""
        return [table for table in self._pizzeria.hall.tables if not table.is_occupied]

    def suggest_table(self, guests_count: int) -> Table:
        """Find first suitable free table."""
        return self._pizzeria.hall.find_free_table(guests_count)

    def list_employees(self) -> list[Employee]:
        """Return employees sorted by id."""
        return sorted(self._pizzeria.employees, key=lambda employee: employee.id)

    def set_employee_active(self, employee_id: int, active: bool) -> Employee:
        """Enable or disable employee."""
        for employee in self._pizzeria.employees:
            if employee.id == employee_id:
                employee.active = active
                return employee
        raise NotFoundError(f"Сотрудник {employee_id} не найден")

    def finance_report(self) -> dict:
        """Return detailed finance report."""
        orders = self.list_orders()
        paid_orders = [order for order in orders if order.is_paid]
        unpaid_orders = [
            order
            for order in orders
            if not order.is_paid and order.status not in (OrderStatus.CANCELED, OrderStatus.COMPLETED)
        ]

        total_salary = round(sum(employee.salary for employee in self._pizzeria.employees if employee.active), 2)
        average_check = round(self._pizzeria.revenue / len(paid_orders), 2) if paid_orders else 0.0
        unpaid_total = round(sum(order.total_price for order in unpaid_orders), 2)

        return {
            "revenue": round(self._pizzeria.revenue, 2),
            "tips_total": round(self._pizzeria.tips_total, 2),
            "collected_total": round(self._pizzeria.revenue + self._pizzeria.tips_total, 2),
            "cash": round(self._pizzeria.order_counter.payment_system.cash_desk.cash_amount, 2),
            "paid_orders": len(paid_orders),
            "unpaid_orders": len(unpaid_orders),
            "average_check": average_check,
            "unpaid_total": unpaid_total,
            "salary_fund": total_salary,
            "projected_balance_after_salary": round(
                self._pizzeria.order_counter.payment_system.cash_desk.cash_amount - total_salary,
                2,
            ),
        }

    def snapshot(self) -> dict:
        """Get compact system snapshot."""
        status_counts: dict[str, int] = {}
        for order in self._pizzeria.orders:
            status_counts[order.status.value] = status_counts.get(order.status.value, 0) + 1

        return {
            "orders_total": len(self._pizzeria.orders),
            "orders_by_status": status_counts,
            "revenue": self._pizzeria.revenue,
            "tips_total": self._pizzeria.tips_total,
            "cash": self._pizzeria.order_counter.payment_system.cash_desk.cash_amount,
            "active_deliveries": len(self._pizzeria.delivery.tasks),
            "free_tables": len(self.list_free_tables()),
            "tables_total": len(self._pizzeria.hall.tables),
        }
