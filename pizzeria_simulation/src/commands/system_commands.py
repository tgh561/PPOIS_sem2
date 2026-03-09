"""System status commands."""
from src.models import PizzeriaState


def print_system_status(state: PizzeriaState) -> None:
    print(f"\nСТАТУС СИСТЕМЫ")
    print(f"Заказов: {len(state.orders)}")
    print(f"Меню: {len(state.order_desk.menu.items)} позиций")

    free_tables = sum(1 for t in state.dining_hall.tables if not t.is_occupied)
    print(f"Столиков: {len(state.dining_hall.tables)} ({free_tables} свободно)")

    print(f"Сотрудников: {len(state.staff_team.employees)}")
    print(
        f"Кухня: {len(state.kitchen.orders_in_queue)}/"
        f"{len(state.kitchen.orders_cooking)}/"
        f"{len(state.kitchen.orders_baked)}"
    )
