"""Зал и столики."""
from dataclasses import dataclass


@dataclass
class Table:
    """Столик в зале."""
    id: int
    capacity: int
    is_occupied: bool


@dataclass
class DiningHall:
    """Зал пиццерии."""
    tables: list[Table]
