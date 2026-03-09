"""Main CLI entry point."""
from src.utils.storage import load_state, save_state
from src.commands import (
    handle_orders_menu,
    handle_kitchen_menu,
    handle_payments_menu,
    handle_hall_menu,
    handle_finance_menu,
    handle_staff_menu,
    print_system_status,
)


def print_main_menu() -> None:
    print("\n" + "=" * 50)
    print("ПИЦЦЕРИЯ — СИМУЛЯТОР")
    print("=" * 50)
    print("1. Заказы")
    print("2. Зал (столики)")
    print("3. Кухня")
    print("4. Финансы")
    print("5. Персонал")
    print("6. Статус системы")
    print("7. Оплаты")
    print("0. Выход")
    print("=" * 50)


def main() -> None:
    state = load_state()

    while True:
        print_main_menu()
        choice = input("Выберите действие (0-7): ").strip()

        if choice == "0":
            print("До свидания!")
            save_state(state)
            break
        elif choice == "1":
            handle_orders_menu(state)
        elif choice == "2":
            handle_hall_menu(state)
        elif choice == "3":
            handle_kitchen_menu(state)
        elif choice == "4":
            handle_finance_menu(state)
        elif choice == "5":
            handle_staff_menu(state)
        elif choice == "6":
            print_system_status(state)
        elif choice == "7":
            handle_payments_menu(state)
        else:
            print("Неверный выбор!")

        input("\nНажмите Enter для продолжения...")
