"""Delivery coordinator model."""
from __future__ import annotations

from dataclasses import dataclass, field

from pizzeria.domain.exceptions import ResourceUnavailableError


@dataclass(slots=True)
class DeliveryTask:
    """Task representing active delivery."""

    order_id: int
    remaining_minutes: int

    def to_dict(self) -> dict:
        """Serialize task."""
        return {
            "order_id": self.order_id,
            "remaining_minutes": self.remaining_minutes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DeliveryTask":
        """Deserialize task."""
        return cls(order_id=int(data["order_id"]), remaining_minutes=int(data["remaining_minutes"]))


@dataclass(slots=True)
class DeliveryCoordinator:
    """Tracks active deliveries."""

    tasks: dict[int, DeliveryTask] = field(default_factory=dict)

    def start(self, order_id: int, duration_minutes: int = 30) -> None:
        """Start delivery for order."""
        if order_id in self.tasks:
            raise ResourceUnavailableError(f"Заказ {order_id} уже находится в доставке")
        self.tasks[order_id] = DeliveryTask(order_id=order_id, remaining_minutes=duration_minutes)

    def tick(self, minutes: int) -> list[int]:
        """Advance delivery simulation and return delivered order ids."""
        delivered: list[int] = []
        for task in self.tasks.values():
            task.remaining_minutes = max(0, task.remaining_minutes - minutes)

        finished = [order_id for order_id, task in self.tasks.items() if task.remaining_minutes == 0]
        for order_id in finished:
            delivered.append(order_id)
            self.tasks.pop(order_id, None)
        return delivered

    def is_in_progress(self, order_id: int) -> bool:
        """Check if order is still in delivery route."""
        return order_id in self.tasks

    def to_dict(self) -> dict:
        """Serialize coordinator."""
        return {"tasks": [task.to_dict() for task in self.tasks.values()]}

    @classmethod
    def from_dict(cls, data: dict) -> "DeliveryCoordinator":
        """Deserialize coordinator."""
        tasks = [DeliveryTask.from_dict(item) for item in data.get("tasks", [])]
        return cls(tasks={task.order_id: task for task in tasks})
