"""Dining hall model."""
from __future__ import annotations

from dataclasses import dataclass, field

from pizzeria.domain.exceptions import NotFoundError, ResourceUnavailableError
from pizzeria.domain.models.table import Table


@dataclass(slots=True)
class Hall:
    """Dining hall with tables."""

    tables: list[Table] = field(default_factory=list)

    def find_table(self, table_number: int) -> Table:
        """Find table by number."""
        for table in self.tables:
            if table.number == table_number:
                return table
        raise NotFoundError(f"Столик {table_number} не найден")

    def find_free_table(self, guests_count: int) -> Table:
        """Find first free table for given guests count."""
        for table in self.tables:
            if not table.is_occupied and table.capacity >= guests_count:
                return table
        raise ResourceUnavailableError("Нет свободного столика для указанного количества гостей")

    def occupy_table(self, table_number: int, order_id: int) -> None:
        """Occupy table."""
        table = self.find_table(table_number)
        table.occupy(order_id)

    def release_table_by_order(self, order_id: int) -> None:
        """Release table connected with order id."""
        for table in self.tables:
            if table.order_id == order_id:
                table.release()
                return

    def to_dict(self) -> dict:
        """Serialize hall."""
        return {"tables": [table.to_dict() for table in self.tables]}

    @classmethod
    def from_dict(cls, data: dict) -> "Hall":
        """Deserialize hall."""
        tables = [Table.from_dict(item) for item in data.get("tables", [])]
        return cls(tables=tables)
