"""Staff management commands."""
from src.models import PizzeriaState


def handle_staff_menu(state: PizzeriaState) -> None:
    print(f"\nПЕРСОНАЛ ({len(state.staff_team.employees)} сотрудников):")
    for emp in state.staff_team.employees:
        print(
            f"{emp.id}. {emp.name} ({emp.role.value}) — "
            f"{emp.base_salary}р + {emp.tips:.2f}р чаевых"
        )
