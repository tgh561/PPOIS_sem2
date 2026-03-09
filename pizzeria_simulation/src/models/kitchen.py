"""Кухня."""
from dataclasses import dataclass


@dataclass
class Kitchen:
    """Кухня пиццерии."""
    orders_in_queue: list[int]
    orders_cooking: list[int]
    orders_baked: list[int]
