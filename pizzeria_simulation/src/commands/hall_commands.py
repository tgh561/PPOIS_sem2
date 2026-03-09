"""Hall management commands."""
from src.models import PizzeriaState


def handle_hall_menu(state: PizzeriaState) -> None:
    free_count = sum(1 for t in state.dining_hall.tables if not t.is_occupied)
    print(f"\nЗАЛ: {free_count} свободных столиков")

    for table in state.dining_hall.tables:
        status = "свободен" if not table.is_occupied else "занят"
        print(f"Столик {table.id} ({table.capacity} мест) — {status}")
