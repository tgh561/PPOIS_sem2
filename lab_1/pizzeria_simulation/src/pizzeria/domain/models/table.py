"""Dining table model."""
from __future__ import annotations

from dataclasses import dataclass

from pizzeria.domain.exceptions import ResourceUnavailableError


@dataclass(slots=True)
class Table:
    """Table in dining hall."""

    number: int
    capacity: int
    is_occupied: bool = False
    order_id: int | None = None

    def occupy(self, order_id: int) -> None:
        """Mark table as occupied by order."""
        if self.is_occupied:
            raise ResourceUnavailableError(f"Столик {self.number} уже занят")
        self.is_occupied = True
        self.order_id = order_id

    def release(self) -> None:
        """Mark table as free."""
        self.is_occupied = False
        self.order_id = None

    def to_dict(self) -> dict:
        """Serialize table."""
        return {
            "number": self.number,
            "capacity": self.capacity,
            "is_occupied": self.is_occupied,
            "order_id": self.order_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Table":
        """Deserialize table."""
        return cls(
            number=int(data["number"]),
            capacity=int(data["capacity"]),
            is_occupied=bool(data.get("is_occupied", False)),
            order_id=data.get("order_id"),
        )
