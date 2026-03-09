"""Пицца и ингредиенты."""
from dataclasses import dataclass

from src.enums import PizzaBase, ToppingCategory


@dataclass
class Topping:
    """Топпинг для пиццы."""
    id: int
    name: str
    price: float
    category: ToppingCategory
    is_available: bool


@dataclass
class PizzaBaseItem:
    """База для пиццы."""
    id: int
    name: str
    base_type: PizzaBase
    price: float


@dataclass
class CustomPizza:
    """Кастомная пицца."""
    base_id: int
    toppings: list[int]
    size: str
