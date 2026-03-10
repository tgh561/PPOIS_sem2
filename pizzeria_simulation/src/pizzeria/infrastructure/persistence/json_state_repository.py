"""JSON state repository."""
from __future__ import annotations

import json
from pathlib import Path

from pizzeria.domain.models import Pizzeria, create_default_pizzeria
from pizzeria.domain.models.menu import MenuItem, create_default_menu


class JsonStateRepository:
    """Persistence adapter for storing pizzeria state in JSON."""

    def __init__(self, filepath: Path):
        self._filepath = filepath

    def load(self) -> Pizzeria:
        """Load pizzeria state or create default one."""
        if not self._filepath.exists():
            return create_default_pizzeria()

        with self._filepath.open("r", encoding="utf-8") as file:
            data = json.load(file)
        pizzeria = Pizzeria.from_dict(data)
        self._merge_missing_menu_items(pizzeria)
        return pizzeria

    @staticmethod
    def _merge_missing_menu_items(pizzeria: Pizzeria) -> None:
        """Merge new default menu positions into persisted state."""
        current_items = pizzeria.order_counter.menu.items
        for item_id, item in create_default_menu().items.items():
            if item_id in current_items:
                continue
            current_items[item_id] = MenuItem.from_dict(item.to_dict())

    def save(self, pizzeria: Pizzeria) -> None:
        """Save pizzeria state."""
        self._filepath.parent.mkdir(parents=True, exist_ok=True)
        with self._filepath.open("w", encoding="utf-8") as file:
            json.dump(pizzeria.to_dict(), file, ensure_ascii=False, indent=2)
