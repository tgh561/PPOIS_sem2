"""Menu models."""
from __future__ import annotations

from dataclasses import dataclass, field

from pizzeria.domain.exceptions import NotFoundError


@dataclass(slots=True)
class MenuItem:
    """Single menu item."""

    id: int
    name: str
    category: str
    price: float
    toppings: list[str] = field(default_factory=list)
    ingredient_requirements: dict[str, float] = field(default_factory=dict)
    is_available: bool = True

    def to_dict(self) -> dict:
        """Serialize menu item."""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "price": self.price,
            "toppings": list(self.toppings),
            "ingredient_requirements": dict(self.ingredient_requirements),
            "is_available": self.is_available,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MenuItem":
        """Deserialize menu item."""
        return cls(
            id=int(data["id"]),
            name=str(data["name"]),
            category=str(data["category"]),
            price=float(data["price"]),
            toppings=list(data.get("toppings", [])),
            ingredient_requirements={k: float(v) for k, v in data.get("ingredient_requirements", {}).items()},
            is_available=bool(data.get("is_available", True)),
        )


@dataclass(slots=True)
class Menu:
    """Menu aggregate with quick access by id."""

    items: dict[int, MenuItem]

    def get_item(self, item_id: int) -> MenuItem:
        """Get menu item by id."""
        item = self.items.get(item_id)
        if item is None:
            raise NotFoundError(f"Позиция меню с идентификатором {item_id} не найдена")
        return item

    def list_pizzas(self) -> list[MenuItem]:
        """List available pizza items."""
        return [item for item in self.items.values() if item.category == "pizza" and item.is_available]

    def list_drinks(self) -> list[MenuItem]:
        """List available drink items."""
        return [item for item in self.items.values() if item.category == "drink" and item.is_available]

    def to_dict(self) -> dict:
        """Serialize menu."""
        return {"items": [item.to_dict() for item in self.items.values()]}

    @classmethod
    def from_dict(cls, data: dict) -> "Menu":
        """Deserialize menu."""
        items = [MenuItem.from_dict(item) for item in data.get("items", [])]
        return cls(items={item.id: item for item in items})


def create_default_menu() -> Menu:
    """Factory for default menu."""
    items = {
        1: MenuItem(
            id=1,
            name="Маргарита",
            category="pizza",
            price=9.5,
            toppings=["моцарелла", "базилик", "томатный соус"],
            ingredient_requirements={
                "тесто": 1,
                "томатный_соус": 0.2,
                "моцарелла": 0.2,
                "базилик": 0.05,
            },
        ),
        2: MenuItem(
            id=2,
            name="Пепперони",
            category="pizza",
            price=11.0,
            toppings=["пепперони", "моцарелла", "томатный соус"],
            ingredient_requirements={
                "тесто": 1,
                "томатный_соус": 0.2,
                "моцарелла": 0.2,
                "пепперони": 0.2,
            },
        ),
        3: MenuItem(
            id=3,
            name="Вегетарианская",
            category="pizza",
            price=10.5,
            toppings=["грибы", "перец", "оливки"],
            ingredient_requirements={
                "тесто": 1,
                "томатный_соус": 0.2,
                "моцарелла": 0.2,
                "грибы": 0.15,
                "перец": 0.1,
                "оливки": 0.1,
            },
        ),
        4: MenuItem(
            id=4,
            name="Четыре сыра",
            category="pizza",
            price=12.0,
            toppings=["моцарелла", "моцарелла", "базилик"],
            ingredient_requirements={
                "тесто": 1,
                "томатный_соус": 0.15,
                "моцарелла": 0.35,
                "базилик": 0.03,
            },
        ),
        5: MenuItem(
            id=5,
            name="Грибная",
            category="pizza",
            price=11.5,
            toppings=["грибы", "моцарелла", "томатный соус"],
            ingredient_requirements={
                "тесто": 1,
                "томатный_соус": 0.2,
                "моцарелла": 0.2,
                "грибы": 0.2,
            },
        ),
        6: MenuItem(
            id=6,
            name="Острая пепперони",
            category="pizza",
            price=12.5,
            toppings=["пепперони", "перец", "моцарелла"],
            ingredient_requirements={
                "тесто": 1,
                "томатный_соус": 0.2,
                "моцарелла": 0.2,
                "пепперони": 0.2,
                "перец": 0.12,
            },
        ),
        7: MenuItem(
            id=7,
            name="Капричоза",
            category="pizza",
            price=12.3,
            toppings=["грибы", "оливки", "пепперони"],
            ingredient_requirements={
                "тесто": 1,
                "томатный_соус": 0.2,
                "моцарелла": 0.2,
                "грибы": 0.15,
                "оливки": 0.12,
                "пепперони": 0.15,
            },
        ),
        8: MenuItem(
            id=8,
            name="Домашняя",
            category="pizza",
            price=11.8,
            toppings=["перец", "грибы", "оливки"],
            ingredient_requirements={
                "тесто": 1,
                "томатный_соус": 0.2,
                "моцарелла": 0.2,
                "перец": 0.1,
                "грибы": 0.12,
                "оливки": 0.1,
            },
        ),
        101: MenuItem(id=101, name="Кола", category="drink", price=2.5),
        102: MenuItem(id=102, name="Вода", category="drink", price=1.8),
        103: MenuItem(id=103, name="Лимонад", category="drink", price=2.7),
        104: MenuItem(id=104, name="Апельсиновый сок", category="drink", price=3.2),
        105: MenuItem(id=105, name="Чай", category="drink", price=2.2),
        106: MenuItem(id=106, name="Кофе", category="drink", price=2.9),
    }
    return Menu(items=items)
