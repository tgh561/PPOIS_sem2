"""Order counter model."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from pizzeria.domain import PizzaSize
from pizzeria.domain.exceptions import ValidationError
from pizzeria.domain.models.menu import Menu, MenuItem
from pizzeria.domain.models.payment import PaymentSystem
from pizzeria.domain.models.pizza import Pizza


@dataclass(slots=True)
class OrderCounter:
    """Order counter with menu and payment system."""

    menu: Menu
    payment_system: PaymentSystem

    def build_pizzas(self, item_ids: list[int], size: PizzaSize, pizza_id_factory: Callable[[], int]) -> list[Pizza]:
        """Build pizza entities from menu item ids."""
        if not item_ids:
            raise ValidationError("Заказ должен содержать минимум одну пиццу")

        pizzas: list[Pizza] = []
        for item_id in item_ids:
            item = self.menu.get_item(item_id)
            if item.category != "pizza":
                raise ValidationError("На этом этапе поддерживаются только пиццы")
            if not item.is_available:
                raise ValidationError(f"Позиция '{item.name}' временно недоступна")

            pizza = Pizza(
                id=pizza_id_factory(),
                name=item.name,
                size=size,
                toppings=list(item.toppings),
                ingredient_requirements=dict(item.ingredient_requirements),
                base_price=item.price,
            )
            pizzas.append(pizza)
        return pizzas

    def build_drinks(self, item_ids: list[int]) -> list[MenuItem]:
        """Build drink items snapshot from menu ids."""
        drinks: list[MenuItem] = []
        for item_id in item_ids:
            item = self.menu.get_item(item_id)
            if item.category != "drink":
                raise ValidationError(f"Позиция '{item.name}' не относится к напиткам")
            if not item.is_available:
                raise ValidationError(f"Позиция '{item.name}' временно недоступна")
            drinks.append(MenuItem.from_dict(item.to_dict()))
        return drinks

    def to_dict(self) -> dict:
        """Serialize order counter."""
        return {
            "menu": self.menu.to_dict(),
            "payment_system": self.payment_system.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "OrderCounter":
        """Deserialize order counter."""
        from pizzeria.domain.models.menu import Menu
        from pizzeria.domain.models.payment import PaymentSystem

        return cls(
            menu=Menu.from_dict(data.get("menu", {})),
            payment_system=PaymentSystem.from_dict(data.get("payment_system", {})),
        )
