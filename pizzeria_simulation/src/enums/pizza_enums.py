"""Перечисления для пиццы."""
from enum import StrEnum


class PizzaBase(StrEnum):
    """Базы для пиццы."""
    CLASSIC = "classic"
    THIN = "thin"
    STUFFED = "stuffed"


class ToppingCategory(StrEnum):
    """Категории топпингов."""
    MEAT = "meat"
    CHEESE = "cheese"
    VEGETABLE = "vegetable"
    SAUCE = "sauce"
