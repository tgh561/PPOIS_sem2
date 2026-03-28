"""Stock and storage model."""
from __future__ import annotations

from dataclasses import dataclass, field

from pizzeria.domain.exceptions import ResourceUnavailableError


@dataclass(slots=True)
class Stock:
    """Storage for ingredients and consumables."""

    ingredients: dict[str, float] = field(default_factory=dict)
    pizza_boxes: int = 0
    receipt_paper_rolls: int = 0

    def has_ingredients(self, required: dict[str, float]) -> bool:
        """Check if required ingredients are available."""
        for name, quantity in required.items():
            if self.ingredients.get(name, 0.0) < quantity:
                return False
        return True

    def consume_ingredients(self, required: dict[str, float]) -> None:
        """Deduct ingredients from stock."""
        if not self.has_ingredients(required):
            raise ResourceUnavailableError("Недостаточно ингредиентов на складе")
        for name, quantity in required.items():
            self.ingredients[name] -= quantity

    def restock_ingredient(self, ingredient_name: str, quantity: float) -> None:
        """Add ingredient quantity."""
        self.ingredients[ingredient_name] = self.ingredients.get(ingredient_name, 0.0) + quantity

    def consume_pizza_box(self) -> None:
        """Use one pizza box."""
        if self.pizza_boxes <= 0:
            raise ResourceUnavailableError("Закончились коробки для пиццы")
        self.pizza_boxes -= 1

    def consume_receipt_paper(self) -> None:
        """Use one receipt paper roll unit."""
        if self.receipt_paper_rolls <= 0:
            raise ResourceUnavailableError("Закончилась чековая лента на складе")
        self.receipt_paper_rolls -= 1

    def to_dict(self) -> dict:
        """Serialize stock."""
        return {
            "ingredients": dict(self.ingredients),
            "pizza_boxes": self.pizza_boxes,
            "receipt_paper_rolls": self.receipt_paper_rolls,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Stock":
        """Deserialize stock."""
        return cls(
            ingredients={k: float(v) for k, v in data.get("ingredients", {}).items()},
            pizza_boxes=int(data.get("pizza_boxes", 0)),
            receipt_paper_rolls=int(data.get("receipt_paper_rolls", 0)),
        )
