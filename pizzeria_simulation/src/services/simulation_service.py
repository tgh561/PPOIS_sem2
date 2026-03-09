"""Сервис симуляции времени."""
import random

from src.models import PizzeriaState, OrderStatus


class SimulationService:
    """Сервис для симуляции времени на кухне."""

    def __init__(self, state: PizzeriaState):
        self.state = state

    def tick(self, minutes: int = 10) -> dict:
        """
        Симулирует прохождение времени.

        Возвращает отчёт о изменениях.
        """
        report = {
            "moved_to_cooking": [],
            "moved_to_baked": [],
            "minutes_passed": minutes,
        }

        if self.state.kitchen.orders_in_queue:
            order_id = self.state.kitchen.orders_in_queue.pop(0)
            self.state.kitchen.orders_cooking.append(order_id)
            report["moved_to_cooking"].append(order_id)

        if self.state.kitchen.orders_cooking and random.random() < 0.3:
            order_id = self.state.kitchen.orders_cooking.pop(0)
            self.state.kitchen.orders_baked.append(order_id)
            report["moved_to_baked"].append(order_id)

        return report

    def get_kitchen_status(self) -> dict:
        """Получает статус кухни."""
        return {
            "in_queue": len(self.state.kitchen.orders_in_queue),
            "cooking": len(self.state.kitchen.orders_cooking),
            "baked": len(self.state.kitchen.orders_baked),
        }

    def add_to_queue(self, order_id: int) -> bool:
        """Добавляет заказ в очередь кухни."""
        if order_id in self.state.kitchen.orders_in_queue:
            return False

        order = next((o for o in self.state.orders if o.id == order_id), None)
        if not order:
            return False

        if order.status not in (OrderStatus.CREATED, OrderStatus.PAID):
            return False

        self.state.kitchen.orders_in_queue.append(order_id)
        return True
