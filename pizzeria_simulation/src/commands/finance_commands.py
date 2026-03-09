"""Finance management commands."""
from src.models import PizzeriaState


def handle_finance_menu(state: PizzeriaState) -> None:
    print(f"\nФИНАНСЫ")
    print(f"Выручка: {state.finance.total_revenue:.2f}р")
    print(f"Чаевые: {state.finance.total_tips:.2f}р")
    print(f"В кассе: {state.order_desk.cash_register.cash_amount:.2f}р")
