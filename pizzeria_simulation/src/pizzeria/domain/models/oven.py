"""Oven model."""
from __future__ import annotations

from dataclasses import dataclass, field

from pizzeria.domain.exceptions import ResourceUnavailableError


@dataclass(slots=True)
class BakingTask:
    """Single pizza baking task."""

    pizza_id: int
    remaining_minutes: int

    def to_dict(self) -> dict:
        """Serialize baking task."""
        return {
            "pizza_id": self.pizza_id,
            "remaining_minutes": self.remaining_minutes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BakingTask":
        """Deserialize baking task."""
        return cls(
            pizza_id=int(data["pizza_id"]),
            remaining_minutes=int(data["remaining_minutes"]),
        )


@dataclass(slots=True)
class Oven:
    """Limited baking resource."""

    id: int
    capacity: int
    is_operational: bool = True
    baking: list[BakingTask] = field(default_factory=list)
    queue: list[BakingTask] = field(default_factory=list)

    def enqueue_pizza(self, pizza_id: int, baking_minutes: int) -> None:
        """Add pizza to baking process or queue."""
        if not self.is_operational:
            raise ResourceUnavailableError(f"Печь {self.id} не работает")

        task = BakingTask(pizza_id=pizza_id, remaining_minutes=baking_minutes)
        if len(self.baking) < self.capacity:
            self.baking.append(task)
        else:
            self.queue.append(task)

    def tick(self, minutes: int) -> tuple[list[int], list[int]]:
        """Advance baking timer by minutes.

        Returns tuple: (ready_pizza_ids, moved_from_queue_ids).
        """
        if minutes <= 0:
            return [], []

        ready: list[int] = []
        for task in self.baking:
            task.remaining_minutes = max(0, task.remaining_minutes - minutes)

        still_baking: list[BakingTask] = []
        for task in self.baking:
            if task.remaining_minutes == 0:
                ready.append(task.pizza_id)
            else:
                still_baking.append(task)
        self.baking = still_baking

        moved_to_baking: list[int] = []
        while self.queue and len(self.baking) < self.capacity:
            next_task = self.queue.pop(0)
            self.baking.append(next_task)
            moved_to_baking.append(next_task.pizza_id)

        return ready, moved_to_baking

    def load(self) -> int:
        """Current oven load (baking + queued)."""
        return len(self.baking) + len(self.queue)

    def to_dict(self) -> dict:
        """Serialize oven."""
        return {
            "id": self.id,
            "capacity": self.capacity,
            "is_operational": self.is_operational,
            "baking": [task.to_dict() for task in self.baking],
            "queue": [task.to_dict() for task in self.queue],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Oven":
        """Deserialize oven."""
        return cls(
            id=int(data["id"]),
            capacity=int(data["capacity"]),
            is_operational=bool(data.get("is_operational", True)),
            baking=[BakingTask.from_dict(item) for item in data.get("baking", [])],
            queue=[BakingTask.from_dict(item) for item in data.get("queue", [])],
        )
