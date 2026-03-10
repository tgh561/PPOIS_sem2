"""CLI application interface."""
from __future__ import annotations

from pizzeria.application.services import PizzeriaService
from pizzeria.domain import CustomerType, DomainError, EmployeeRole, OrderStatus, PaymentType, PizzaSize
from pizzeria.domain.models import Order

ORDER_STATUS_RU: dict[OrderStatus, str] = {
    OrderStatus.CREATED: "создан",
    OrderStatus.CONFIRMED: "подтверждён",
    OrderStatus.PREPARING: "подготовка",
    OrderStatus.BAKING: "выпекается",
    OrderStatus.READY: "готов",
    OrderStatus.OUT_FOR_DELIVERY: "в доставке",
    OrderStatus.COMPLETED: "выполнен",
    OrderStatus.CANCELED: "отменён",
}

CUSTOMER_TYPE_RU: dict[CustomerType, str] = {
    CustomerType.DINE_IN: "в зале",
    CustomerType.DELIVERY: "доставка",
}

PAYMENT_TYPE_RU: dict[PaymentType, str] = {
    PaymentType.CASH: "наличные",
    PaymentType.CARD: "карта",
}

EMPLOYEE_ROLE_RU: dict[EmployeeRole, str] = {
    EmployeeRole.COOK: "повар",
    EmployeeRole.COURIER: "курьер",
    EmployeeRole.CASHIER: "кассир",
    EmployeeRole.MANAGER: "менеджер",
}


class CliApp:
    """Simple CLI application wrapper."""

    def __init__(self, service: PizzeriaService):
        self._service = service

    def run(self) -> None:
        """Run CLI loop."""
        while True:
            self._print_main_menu()
            choice = input("Выберите раздел (0-8): ").strip()

            if choice == "0":
                print("Состояние сохранено. До свидания!")
                return

            try:
                self._handle_main_choice(choice)
            except DomainError as error:
                print(f"Ошибка: {error}")
            except ValueError:
                print("Неверный ввод")

            input("\nНажмите ввод для продолжения...")

    def _handle_main_choice(self, choice: str) -> None:
        if choice == "1":
            self._orders_menu()
        elif choice == "2":
            self._hall_menu()
        elif choice == "3":
            self._kitchen_menu()
        elif choice == "4":
            self._delivery_menu()
        elif choice == "5":
            self._payments_menu()
        elif choice == "6":
            self._finance_menu()
        elif choice == "7":
            self._staff_menu()
        elif choice == "8":
            self._show_system_status()
        else:
            print("Неизвестный пункт меню")

    @staticmethod
    def _print_main_menu() -> None:
        print("\n" + "=" * 62)
        print("ПИЦЦЕРИЯ — ГЛАВНОЕ МЕНЮ")
        print("=" * 62)
        print("1. Заказы")
        print("2. Зал (столики)")
        print("3. Кухня")
        print("4. Доставка")
        print("5. Оплаты")
        print("6. Финансы")
        print("7. Персонал")
        print("8. Статус системы")
        print("0. Выход")
        print("=" * 62)

    @staticmethod
    def _print_menu_header(title: str) -> None:
        print("\n" + "-" * 62)
        print(title)
        print("-" * 62)

    @staticmethod
    def _parse_ids(raw: str) -> list[int]:
        return [int(chunk.strip()) for chunk in raw.split(",") if chunk.strip()]

    @staticmethod
    def _ask_pizza_size() -> PizzaSize:
        print("Размер пиццы: 1=маленькая, 2=средняя, 3=большая")
        mapping = {"1": PizzaSize.SMALL, "2": PizzaSize.MEDIUM, "3": PizzaSize.LARGE}
        selected = input("Выберите размер: ").strip()
        if selected not in mapping:
            raise ValueError("Неизвестный размер")
        return mapping[selected]

    @staticmethod
    def _ask_payment_type() -> PaymentType:
        print("Тип оплаты: 1=наличные, 2=карта")
        mapping = {"1": PaymentType.CASH, "2": PaymentType.CARD}
        selected = input("Выберите тип оплаты: ").strip()
        if selected not in mapping:
            raise ValueError("Неизвестный тип оплаты")
        return mapping[selected]

    def _format_order_line(self, order: Order) -> str:
        order_type = CUSTOMER_TYPE_RU[order.customer_type]
        order_status = ORDER_STATUS_RU[order.status]
        payment = PAYMENT_TYPE_RU[order.payment_type]
        paid = "да" if order.is_paid else "нет"
        target = f"столик {order.table_number}" if order.table_number else f"адрес: {order.delivery_address}"
        composition = f"пицц: {len(order.pizzas)}, напитков: {len(order.drinks)}"
        return (
            f"№{order.id} | {order_type} | {order_status} | {composition} | оплачен: {paid} | "
            f"{order.total_price:.2f} руб. | {payment} | {target}"
        )

    def _print_orders(self, orders: list[Order], title: str) -> None:
        self._print_menu_header(title)
        if not orders:
            print("Список пуст")
            return
        for order in orders:
            print(self._format_order_line(order))

    def _select_order_id(self, orders: list[Order], prompt: str) -> int | None:
        if not orders:
            print("Подходящих заказов нет")
            return None

        self._print_orders(orders, "Доступные заказы")
        selected = input(f"{prompt} (0 - отмена): ").strip()
        if selected == "0":
            return None

        order_id = int(selected)
        order_ids = {order.id for order in orders}
        if order_id not in order_ids:
            raise ValueError("Выбран заказ, которого нет в списке")
        return order_id

    def _print_pizza_menu(self) -> None:
        self._print_menu_header("Меню пицц")
        for item in self._service.pizzeria.order_counter.menu.list_pizzas():
            print(f"{item.id}. {item.name:<20} {item.price:>6.2f} руб.")

    def _print_drinks_menu(self) -> None:
        self._print_menu_header("Меню напитков")
        drinks = self._service.pizzeria.order_counter.menu.list_drinks()
        if not drinks:
            print("Напитков в меню нет")
            return
        for item in drinks:
            print(f"{item.id}. {item.name:<20} {item.price:>6.2f} руб.")

    def _orders_menu(self) -> None:
        while True:
            self._print_menu_header("ЗАКАЗЫ")
            print("1. Новый заказ в зале")
            print("2. Новый заказ на доставку")
            print("3. Показать все заказы")
            print("4. Подтвердить заказ")
            print("5. Отправить заказ на кухню")
            print("6. Отменить заказ")
            print("7. Завершить заказ")
            print("0. Назад")

            choice = input("Выберите действие: ").strip()

            if choice == "0":
                return
            if choice == "1":
                self._create_dine_in_order()
            elif choice == "2":
                self._create_delivery_order()
            elif choice == "3":
                self._print_orders(self._service.list_orders(), "Все заказы")
            elif choice == "4":
                self._confirm_order()
            elif choice == "5":
                self._send_order_to_kitchen()
            elif choice == "6":
                self._cancel_order()
            elif choice == "7":
                self._complete_order_from_menu()
            else:
                print("Неверный выбор")

    def _create_dine_in_order(self) -> None:
        free_tables = self._service.list_free_tables()
        if not free_tables:
            print("Свободных столиков нет")
            return

        self._print_menu_header("Свободные столики")
        for table in free_tables:
            print(f"Столик {table.number}: {table.capacity} мест")

        guests_count = int(input("Количество гостей: ").strip())
        table_input = input("Номер столика (0 - подобрать автоматически): ").strip()

        if table_input == "0":
            selected_table = self._service.suggest_table(guests_count)
            table_number = selected_table.number
            print(f"Подобран столик {table_number}")
        else:
            table_number = int(table_input)
            selected_table = next((t for t in free_tables if t.number == table_number), None)
            if selected_table is None:
                raise ValueError("Указанный столик недоступен")
            if selected_table.capacity < guests_count:
                raise ValueError("Вместимость столика меньше количества гостей")

        self._print_pizza_menu()
        pizza_ids = self._parse_ids(input("Номера пицц (через запятую): ").strip())
        self._print_drinks_menu()
        drink_ids = self._parse_ids(input("Номера напитков (через запятую, Enter - без напитков): ").strip())
        size = self._ask_pizza_size()
        payment_type = self._ask_payment_type()

        order = self._service.create_dine_in_order(
            table_number=table_number,
            guests_count=guests_count,
            pizza_item_ids=pizza_ids,
            drink_item_ids=drink_ids,
            size=size,
            payment_type=payment_type,
        )
        print(f"Заказ №{order.id} создан. Сумма: {order.total_price:.2f} руб.")

    def _create_delivery_order(self) -> None:
        self._print_pizza_menu()
        address = input("Адрес доставки: ").strip()
        phone = input("Телефон: ").strip()
        pizza_ids = self._parse_ids(input("Номера пицц (через запятую): ").strip())
        self._print_drinks_menu()
        drink_ids = self._parse_ids(input("Номера напитков (через запятую, Enter - без напитков): ").strip())
        size = self._ask_pizza_size()
        payment_type = self._ask_payment_type()

        order = self._service.create_delivery_order(
            delivery_address=address,
            delivery_phone=phone,
            pizza_item_ids=pizza_ids,
            drink_item_ids=drink_ids,
            size=size,
            payment_type=payment_type,
        )
        print(f"Заказ на доставку №{order.id} создан. Сумма: {order.total_price:.2f} руб.")

    def _confirm_order(self) -> None:
        order_id = self._select_order_id(self._service.list_orders_for_confirmation(), "Номер заказа для подтверждения")
        if order_id is None:
            return

        order = self._service.confirm_order(order_id)
        print(f"Заказ №{order.id} подтверждён")

    def _send_order_to_kitchen(self) -> None:
        order_id = self._select_order_id(self._service.list_orders_for_kitchen(), "Номер заказа для кухни")
        if order_id is None:
            return

        order = self._service.send_order_to_kitchen(order_id)
        print(f"Заказ №{order.id} отправлен на кухню")

    def _cancel_order(self) -> None:
        candidates = self._service.list_active_orders()
        order_id = self._select_order_id(candidates, "Номер заказа для отмены")
        if order_id is None:
            return

        confirm = input("Точно отменить заказ? (д/н): ").strip().lower()
        if confirm not in ("д", "y", "yes"):
            print("Отмена операции")
            return

        order = self._service.cancel_order(order_id)
        print(f"Заказ №{order.id} отменён")

    def _complete_order_from_menu(self) -> None:
        candidates = self._service.list_orders_for_completion()
        order_id = self._select_order_id(candidates, "Номер заказа для завершения")
        if order_id is None:
            return

        order = self._service.complete_order(order_id)
        print(f"Заказ №{order.id} завершён")

    def _hall_menu(self) -> None:
        while True:
            self._print_menu_header("ЗАЛ")
            print("1. Показать столики")
            print("2. Подобрать столик по количеству гостей")
            print("0. Назад")

            choice = input("Выберите действие: ").strip()
            if choice == "0":
                return
            if choice == "1":
                self._show_tables()
            elif choice == "2":
                guests = int(input("Количество гостей: ").strip())
                table = self._service.suggest_table(guests)
                print(f"Подходит столик {table.number} ({table.capacity} мест)")
            else:
                print("Неверный выбор")

    def _show_tables(self) -> None:
        self._print_menu_header("Состояние столиков")
        for table in self._service.pizzeria.hall.tables:
            status = "занят" if table.is_occupied else "свободен"
            order_info = f", заказ №{table.order_id}" if table.order_id else ""
            print(f"Столик {table.number} ({table.capacity} мест): {status}{order_info}")

    def _kitchen_menu(self) -> None:
        while True:
            self._print_menu_header("КУХНЯ")
            print("1. Заказы в работе кухни")
            print("2. Готовые и выполненные заказы")
            print("3. Симулировать 10 минут готовки")
            print("4. Состояние печей")
            print("5. Склад")
            print("0. Назад")

            choice = input("Выберите действие: ").strip()
            if choice == "0":
                return
            if choice == "1":
                self._print_orders(self._service.list_orders_in_kitchen(), "В работе кухни")
            elif choice == "2":
                self._print_orders(self._service.list_ready_and_completed_orders(), "Готовые и выполненные заказы")
            elif choice == "3":
                ready_ids = self._service.tick_kitchen(minutes=10)
                if ready_ids:
                    print(f"После симуляции готовы заказы: {ready_ids}")
                else:
                    print("Новых готовых заказов нет")
                ovens = self._service.pizzeria.kitchen.snapshot()["ovens"]
                queued = sum(int(oven["queue"]) for oven in ovens)
                baking = sum(int(oven["baking"]) for oven in ovens)
                if queued > 0:
                    print(f"В очереди печей ещё {queued} пицц — потребуется дополнительное время симуляции")
                elif baking > 0:
                    print(f"В печах ещё выпекаются {baking} пицц")
                else:
                    print("Все печи свободны")
            elif choice == "4":
                self._show_ovens()
            elif choice == "5":
                self._show_stock()
            else:
                print("Неверный выбор")

    def _show_ovens(self) -> None:
        self._print_menu_header("Состояние печей")
        snapshot = self._service.pizzeria.kitchen.snapshot()["ovens"]
        for oven in snapshot:
            working = "работает" if oven["is_operational"] else "не работает"
            print(f"Печь {oven['id']}: {working}, выпекается={oven['baking']}, очередь={oven['queue']}")

    def _show_stock(self) -> None:
        self._print_menu_header("Склад")
        stock = self._service.pizzeria.kitchen.stock
        for ingredient, quantity in stock.ingredients.items():
            print(f"{ingredient}: {quantity:.2f}")
        print(f"Коробки для пиццы: {stock.pizza_boxes}")
        print(f"Чековая лента: {stock.receipt_paper_rolls}")

    def _delivery_menu(self) -> None:
        while True:
            self._print_menu_header("ДОСТАВКА")
            print("1. Готовые заказы на доставку")
            print("2. Начать доставку")
            print("3. Активные доставки")
            print("4. Симулировать 10 минут доставки")
            print("5. Доставлены, ждут оплату")
            print("0. Назад")

            choice = input("Выберите действие: ").strip()
            if choice == "0":
                return
            if choice == "1":
                self._print_orders(self._service.list_ready_for_delivery(), "Готовы к отправке")
            elif choice == "2":
                order_id = self._select_order_id(self._service.list_ready_for_delivery(), "Номер заказа для доставки")
                if order_id is None:
                    continue
                order = self._service.start_delivery(order_id)
                print(f"Заказ №{order.id} передан курьеру")
            elif choice == "3":
                self._show_active_deliveries()
            elif choice == "4":
                delivered_ids = self._service.tick_delivery(minutes=10)
                if delivered_ids:
                    print(f"Курьер прибыл по заказам: {delivered_ids}")
                else:
                    print("Новых доставленных заказов нет")
            elif choice == "5":
                self._print_orders(self._service.list_arrived_delivery_unpaid(), "Доставлены и ждут оплату")
            else:
                print("Неверный выбор")

    def _show_active_deliveries(self) -> None:
        self._print_menu_header("Активные доставки")
        active = self._service.list_active_deliveries()
        if not active:
            print("Активных доставок нет")
            return

        for order, remaining in active:
            print(f"Заказ №{order.id}: осталось {remaining} мин, адрес: {order.delivery_address}")

    def _payments_menu(self) -> None:
        while True:
            self._print_menu_header("ОПЛАТЫ")
            print("1. Показать заказы к оплате")
            print("2. Оплатить заказ")
            print("0. Назад")

            choice = input("Выберите действие: ").strip()
            if choice == "0":
                return
            if choice == "1":
                self._print_orders(self._service.list_orders_for_payment(), "Ожидают оплату")
            elif choice == "2":
                self._pay_order()
            else:
                print("Неверный выбор")

    def _pay_order(self) -> None:
        candidates = self._service.list_orders_for_payment()
        order_id = self._select_order_id(candidates, "Номер заказа для оплаты")
        if order_id is None:
            return

        order = self._service.pay_order(order_id=order_id)
        print(f"Заказ №{order.id} оплачен ({PAYMENT_TYPE_RU[order.payment_type]})")
        if order.tip_amount > 0:
            print(
                f"Оставлены чаевые: {order.tip_percent}% ({order.tip_amount:.2f} руб.), "
                f"итого +{order.tip_amount:.2f} руб., к оплате {order.paid_amount:.2f} руб."
            )
        else:
            print(f"Чаевые не оставлены. К оплате {order.paid_amount:.2f} руб.")

    def _finance_menu(self) -> None:
        while True:
            self._print_menu_header("ФИНАНСЫ")
            print("1. Краткий финансовый отчёт")
            print("2. Отчёт по оплатам")
            print("3. Фонд зарплаты")
            print("0. Назад")

            choice = input("Выберите действие: ").strip()
            if choice == "0":
                return
            if choice == "1":
                self._show_finance_summary()
            elif choice == "2":
                self._show_payment_summary()
            elif choice == "3":
                self._show_salary_summary()
            else:
                print("Неверный выбор")

    def _show_finance_summary(self) -> None:
        report = self._service.finance_report()
        self._print_menu_header("Финансовый отчёт")
        print(f"Выручка: {report['revenue']:.2f} руб.")
        print(f"Чаевые: {report['tips_total']:.2f} руб.")
        print(f"Получено всего (выручка + чаевые): {report['collected_total']:.2f} руб.")
        print(f"Наличные в кассе: {report['cash']:.2f} руб.")
        print(f"Средний чек: {report['average_check']:.2f} руб.")
        print(f"Неоплаченные заказы: {report['unpaid_orders']} шт. на {report['unpaid_total']:.2f} руб.")

    def _show_payment_summary(self) -> None:
        report = self._service.finance_report()
        self._print_menu_header("Отчёт по оплатам")
        print(f"Оплаченных заказов: {report['paid_orders']}")
        print(f"Неоплаченных заказов: {report['unpaid_orders']}")
        self._print_orders(self._service.list_orders_for_payment(), "Список заказов к оплате")

    def _show_salary_summary(self) -> None:
        report = self._service.finance_report()
        self._print_menu_header("Фонд зарплаты")
        print(f"Фонд активных сотрудников: {report['salary_fund']:.2f} руб.")
        print(f"Остаток после выплаты зарплат: {report['projected_balance_after_salary']:.2f} руб.")

    def _staff_menu(self) -> None:
        while True:
            self._print_menu_header("ПЕРСОНАЛ")
            print("1. Показать сотрудников")
            print("2. Изменить активность сотрудника")
            print("0. Назад")

            choice = input("Выберите действие: ").strip()
            if choice == "0":
                return
            if choice == "1":
                self._show_staff()
            elif choice == "2":
                self._toggle_staff_activity()
            else:
                print("Неверный выбор")

    def _show_staff(self) -> None:
        self._print_menu_header("Сотрудники")
        for employee in self._service.list_employees():
            role = EMPLOYEE_ROLE_RU[employee.role]
            status = "активен" if employee.active else "неактивен"
            print(f"{employee.id}. {employee.name} | {role} | {status} | зарплата {employee.salary:.2f} руб.")

    def _toggle_staff_activity(self) -> None:
        self._show_staff()
        employee_id = int(input("ID сотрудника: ").strip())
        mode = input("Сделать активным? (д/н): ").strip().lower()
        active = mode in ("д", "y", "yes")
        employee = self._service.set_employee_active(employee_id, active)
        status = "активен" if employee.active else "неактивен"
        print(f"Сотрудник {employee.name} теперь {status}")

    def _show_system_status(self) -> None:
        snapshot = self._service.snapshot()
        self._print_menu_header("СТАТУС СИСТЕМЫ")
        print(f"Заказов всего: {snapshot['orders_total']}")
        print(f"Столиков свободно: {snapshot['free_tables']} из {snapshot['tables_total']}")
        print(f"Активных доставок: {snapshot['active_deliveries']}")
        print(f"Выручка: {snapshot['revenue']:.2f} руб.")
        print(f"Чаевые: {snapshot['tips_total']:.2f} руб.")
        print(f"Наличные: {snapshot['cash']:.2f} руб.")
        print("Заказы по статусам:")
        for status in OrderStatus:
            count = snapshot["orders_by_status"].get(status.value, 0)
            print(f"  - {ORDER_STATUS_RU[status]}: {count}")
