"""Pizza domain model."""
from __future__ import annotations

from dataclasses import dataclass

from pizzeria.domain import PizzaSize, PizzaStatus

SIZE_MULTIPLIER: dict[PizzaSize, float] = {
    PizzaSize.SMALL: 0.85,
    PizzaSize.MEDIUM: 1.0,
    PizzaSize.LARGE: 1.25,
}


@dataclass(slots=True)
class Pizza:
    """Pizza entity used inside orders."""

    id: int
    name: str
    size: PizzaSize
    toppings: list[str]
    ingredient_requirements: dict[str, float]
    base_price: float
    status: PizzaStatus = PizzaStatus.CREATED
    remaining_cooking_time: int = 0

    @property
    def price(self) -> float:
        """Calculated pizza price based on selected size."""
        multiplier = SIZE_MULTIPLIER[self.size]
        return round(self.base_price * multiplier, 2)

    def mark_preparing(self) -> None:
        """Move pizza to preparing state."""
        self.status = PizzaStatus.PREPARING

    def start_baking(self, baking_minutes: int) -> None:
        """Move pizza to baking state."""
        self.status = PizzaStatus.BAKING
        self.remaining_cooking_time = baking_minutes

    def mark_ready(self) -> None:
        """Mark pizza as ready."""
        self.status = PizzaStatus.READY
        self.remaining_cooking_time = 0

    def to_dict(self) -> dict:
        """Serialize pizza to JSON-compatible dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "size": self.size.value,
            "toppings": list(self.toppings),
            "ingredient_requirements": dict(self.ingredient_requirements),
            "base_price": self.base_price,
            "status": self.status.value,
            "remaining_cooking_time": self.remaining_cooking_time,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Pizza":
        """Deserialize pizza from dictionary."""
        return cls(
            id=int(data["id"]),
            name=str(data["name"]),
            size=PizzaSize(data["size"]),
            toppings=list(data.get("toppings", [])),
            ingredient_requirements={k: float(v) for k, v in data.get("ingredient_requirements", {}).items()},
            base_price=float(data["base_price"]),
            status=PizzaStatus(data.get("status", PizzaStatus.CREATED.value)),
            remaining_cooking_time=int(data.get("remaining_cooking_time", 0)),
        )
