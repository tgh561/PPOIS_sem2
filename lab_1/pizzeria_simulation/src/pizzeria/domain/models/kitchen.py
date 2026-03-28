"""Kitchen model."""
from __future__ import annotations

from dataclasses import dataclass, field

from pizzeria.domain.exceptions import ResourceUnavailableError
from pizzeria.domain.models.oven import Oven
from pizzeria.domain.models.pizza import Pizza
from pizzeria.domain.models.stock import Stock


@dataclass(slots=True)
class Kitchen:
    """Kitchen aggregate containing ovens and stock."""

    ovens: list[Oven]
    stock: Stock
    preparation_table_capacity: int = 4

    def _pick_oven(self) -> Oven:
        operational = [oven for oven in self.ovens if oven.is_operational]
        if not operational:
            raise ResourceUnavailableError("Нет доступных работающих печей")
        return min(operational, key=lambda oven: oven.load())

    def enqueue_pizza(self, pizza: Pizza, baking_minutes: int = 12) -> int:
        """Prepare pizza and enqueue it for baking."""
        self.stock.consume_ingredients(pizza.ingredient_requirements)
        pizza.mark_preparing()
        pizza.start_baking(baking_minutes)

        oven = self._pick_oven()
        oven.enqueue_pizza(pizza_id=pizza.id, baking_minutes=baking_minutes)
        return oven.id

    def tick(self, minutes: int, pizza_by_id: dict[int, Pizza]) -> list[int]:
        """Advance kitchen simulation and return ready pizza ids."""
        ready: list[int] = []
        for oven in self.ovens:
            ready_ids, _ = oven.tick(minutes)
            for pizza_id in ready_ids:
                pizza = pizza_by_id.get(pizza_id)
                if pizza is None:
                    continue
                pizza.mark_ready()
                self.stock.consume_pizza_box()
                ready.append(pizza_id)
        return ready

    def snapshot(self) -> dict:
        """Get kitchen status snapshot."""
        return {
            "ovens": [
                {
                    "id": oven.id,
                    "baking": len(oven.baking),
                    "queue": len(oven.queue),
                    "is_operational": oven.is_operational,
                }
                for oven in self.ovens
            ]
        }

    def to_dict(self) -> dict:
        """Serialize kitchen."""
        return {
            "ovens": [oven.to_dict() for oven in self.ovens],
            "stock": self.stock.to_dict(),
            "preparation_table_capacity": self.preparation_table_capacity,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Kitchen":
        """Deserialize kitchen."""
        ovens = [Oven.from_dict(item) for item in data.get("ovens", [])]
        stock = Stock.from_dict(data.get("stock", {}))
        return cls(
            ovens=ovens,
            stock=stock,
            preparation_table_capacity=int(data.get("preparation_table_capacity", 4)),
        )
