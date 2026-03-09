"""Order management commands."""
from src.models import PizzeriaState, Order, OrderItem, OrderStatus, OrderType, Menu
from src.menus import print_grouped_menu, show_pizza_details


def print_orders_menu() -> None:
    print("\n" + "=" * 40)
    print("МЕНЮ ЗАКАЗОВ")
    print("=" * 40)
    print("1. Новый заказ на месте")
    print("2. Новый заказ с доставкой")
    print("3. Список активных заказов")
    print("4. Изменить статус заказа")
    print("5. Подать заказ к столику")
    print("6. Начать доставку")
    print("7. Завершить заказ (гость ушёл)")
    print("0. Назад")
    print("=" * 40)


def handle_orders_menu(state: PizzeriaState) -> None:
    while True:
        print_orders_menu()
        choice = input("Выберите действие: ").strip()

        if choice == "0":
            break
        elif choice == "1":
            create_on_site_order(state)
        elif choice == "2":
            create_delivery_order(state)
        elif choice == "3":
            show_active_orders(state)
        elif choice == "4":
            change_order_status(state)
        elif choice == "5":
            serve_order(state)
        elif choice == "6":
            start_delivery(state)
        elif choice == "7":
            complete_order(state)
        else:
            print("Неверный выбор!")


def create_on_site_order(state: PizzeriaState) -> None:
    free_tables = [(t.id, t.capacity) for t in state.dining_hall.tables if not t.is_occupied]

    if not free_tables:
        print("Все столики заняты!")
        return

    print("\nДОСТУПНЫЕ СТОЛИКИ:")
    for table_id, capacity in free_tables:
        print(f"  Столик {table_id} ({capacity} мест)")

    try:
        table_id = int(input("Выберите номер столика: "))
        if table_id not in [t[0] for t in free_tables]:
            print("Столик занят или не существует!")
            return

        show_grouped_menu_with_details(state.order_desk.menu)
        order = create_order_from_input(
            state,
            table_id=table_id,
            order_type=OrderType.ON_SITE,
        )
        state.orders.append(order)

        for table in state.dining_hall.tables:
            if table.id == table_id:
                table.is_occupied = True
                break

        print(f"Заказ #{order.id} создан! Сумма: {order.total_price:.2f}р")
        print("Заказ отправлен на кухню.")

    except ValueError:
        print("Неверный ввод!")


def create_delivery_order(state: PizzeriaState) -> None:
    address = input("Адрес доставки: ").strip()
    if not address:
        print("Адрес обязателен!")
        return

    phone = input("Номер телефона: ").strip()

    show_grouped_menu_with_details(state.order_desk.menu)
    order = create_order_from_input(
        state,
        delivery_address=address,
        customer_phone=phone,
        order_type=OrderType.DELIVERY,
    )
    state.orders.append(order)
    print(f"Заказ на доставку #{order.id} создан! Сумма: {order.total_price:.2f}р")
    print("Заказ отправлен на кухню.")


def show_grouped_menu_with_details(menu: Menu) -> None:
    print_grouped_menu(menu.items)
    
    while True:
        print("\nВведите ID пиццы для просмотра состава (или Enter для продолжения):")
        choice = input("> ").strip()
        
        if not choice:
            break
        
        try:
            pizza_id = int(choice)
            if 1 <= pizza_id <= 8:
                print(show_pizza_details(pizza_id))
            else:
                print("Введите ID пиццы (1-8)")
        except ValueError:
            print("Введите число")


def create_order_from_input(
    state: PizzeriaState,
    table_id: int | None = None,
    delivery_address: str | None = None,
    customer_phone: str | None = None,
    order_type: OrderType = OrderType.ON_SITE,
) -> Order:
    items_input = input("Позиции (1:2,3:1 - ID:количество): ").strip()
    if not items_input:
        raise ValueError("Позиции не указаны!")

    order_items: list[OrderItem] = []
    total_price = 0.0

    for item_spec in items_input.split(","):
        try:
            menu_item_id, qty = map(int, item_spec.strip().split(":"))
            menu_item = next(
                (i for i in state.order_desk.menu.items if i.id == menu_item_id),
                None,
            )

            if not menu_item:
                print(f"Позиция {menu_item_id} не найдена, пропускаем")
                continue

            if not menu_item.is_available:
                print(f"{menu_item.name} недоступна, пропускаем")
                continue

            item = OrderItem(
                id=state.next_id,
                menu_item_id=menu_item.id,
                quantity=qty,
                unit_price=menu_item.price,
                total_price=menu_item.price * qty,
            )
            order_items.append(item)
            total_price += item.total_price
            state.next_id += 1

        except (ValueError, IndexError):
            print(f"Неверный формат '{item_spec}', пропускаем")
            continue

    if not order_items:
        raise ValueError("Нет доступных позиций!")

    order = Order(
        id=state.next_id,
        type=order_type,
        customer_phone=customer_phone,
        table_id=table_id,
        delivery_address=delivery_address,
        items=order_items,
        status=OrderStatus.CREATED,
        created_at="2026-03-09T20:30:00",
        estimated_ready_time=None,
        total_price=total_price,
        tips_amount=0.0,
    )
    state.next_id += 1
    return order


def show_active_orders(state: PizzeriaState) -> None:
    active_orders = [
        o for o in state.orders
        if o.status not in (OrderStatus.COMPLETED, OrderStatus.CANCELLED)
    ]

    if not active_orders:
        print("\nНет активных заказов")
        return

    print(f"\nАКТИВНЫЕ ЗАКАЗЫ ({len(active_orders)}):")
    for order in active_orders:
        type_str = "На месте" if order.type == OrderType.ON_SITE else "Доставка"
        table_info = (
            f"Столик {order.table_id}"
            if order.table_id
            else f"Адрес: {order.delivery_address}"
        )
        paid_status = "ОПЛАЧЕН" if order.status == OrderStatus.PAID else "НЕ ОПЛАЧЕН"
        delivery_info = ""
        if order.type == OrderType.DELIVERY and order.delivery_ticks > 0:
            delivery_info = f" | Доставка: {order.delivery_ticks}/3 тика"
        print(f"#{order.id} | {type_str} | {table_info} | {order.status.value} | {order.total_price:.2f}р | {paid_status}{delivery_info}")


def change_order_status(state: PizzeriaState) -> None:
    show_active_orders(state)

    try:
        order_id = int(input("\nID заказа: "))
        order = next((o for o in state.orders if o.id == order_id), None)

        if not order:
            print("Заказ не найден!")
            return

        print(f"Текущий статус: {order.status.value}")
        print("\nДоступные статусы:")
        print("  created, in_queue, cooking, ready, served, out_for_delivery, delivering, paid, completed, cancelled")
        
        new_status = input("Новый статус: ").strip().lower()

        if hasattr(OrderStatus, new_status.upper()):
            order.status = OrderStatus(new_status.upper())
            print(f"Статус изменён на {order.status.value}")
        else:
            print("Неверный статус!")

    except ValueError:
        print("Неверный ввод!")


def serve_order(state: PizzeriaState) -> None:
    ready_orders = [
        o for o in state.orders
        if o.status == OrderStatus.READY
        and o.type == OrderType.ON_SITE
        and o.table_id is not None
    ]

    if not ready_orders:
        print("Нет готовых заказов для подачи")
        print("Сначала приготовьте заказ на кухне")
        return

    print("\nГОТОВЫЕ ЗАКАЗЫ:")
    for order in ready_orders:
        print(f"#{order.id} | Столик {order.table_id} | {order.total_price:.2f}р")

    try:
        order_id = int(input("ID заказа для подачи: "))
        order = next((o for o in ready_orders if o.id == order_id), None)

        if not order:
            print("Заказ не найден!")
            return

        order.status = OrderStatus.SERVED
        print(f"Заказ #{order.id} подан к столику {order.table_id}!")
        print("Перейдите к оплате.")

    except ValueError:
        print("Неверный ввод!")


def start_delivery(state: PizzeriaState) -> None:
    ready_orders = [
        o for o in state.orders
        if o.status == OrderStatus.READY
        and o.type == OrderType.DELIVERY
    ]

    if not ready_orders:
        print("Нет готовых заказов для доставки")
        return

    print("\nГОТОВЫ К ДОСТАВКЕ:")
    for order in ready_orders:
        print(f"#{order.id} | {order.delivery_address} | {order.total_price:.2f}р")

    try:
        order_id = int(input("ID заказа для начала доставки: "))
        order = next((o for o in ready_orders if o.id == order_id), None)

        if not order:
            print("Заказ не найден!")
            return

        order.status = OrderStatus.OUT_FOR_DELIVERY
        order.delivery_started_at = "2026-03-09T21:00:00"
        order.delivery_ticks = 0
        print(f"Доставка началась для заказа #{order.id}")
        print("Используйте симуляцию времени для доставки (3 тика = 30 минут)")

    except ValueError:
        print("Неверный ввод!")


def complete_order(state: PizzeriaState) -> None:
    completable_orders = [
        o for o in state.orders
        if o.status in (OrderStatus.SERVED, OrderStatus.PAID)
        and o.type == OrderType.ON_SITE
        and o.table_id is not None
    ]

    delivery_completable = [
        o for o in state.orders
        if o.status == OrderStatus.PAID
        and o.type == OrderType.DELIVERY
        and o.delivery_ticks >= 3
    ]

    all_completable = completable_orders + delivery_completable

    if not all_completable:
        print("Нет заказов для завершения")
        print("На месте: заказ должен быть подан")
        print("Доставка: заказ должен быть оплачен и доставлен (3 тика)")
        return

    print("\nЗАКАЗЫ ДОСТУПНЫЕ ДЛЯ ЗАВЕРШЕНИЯ:")
    for order in all_completable:
        paid_status = "ОПЛАЧЕН" if order.status == OrderStatus.PAID else "НЕ ОПЛАЧЕН"
        print(f"#{order.id} | {order.type.value} | {order.total_price:.2f}р | {paid_status}")

    try:
        order_id = int(input("ID заказа для завершения: "))
        order = next((o for o in all_completable if o.id == order_id), None)

        if not order:
            print("Заказ не найден!")
            return

        if order.status != OrderStatus.PAID:
            print("Заказ не оплачен!")
            confirm = input("Завершить несмотря на это? (y/n): ").strip().lower()
            if confirm != "y":
                print("Отменено")
                return

        order.status = OrderStatus.COMPLETED

        if order.table_id:
            table = next(
                (t for t in state.dining_hall.tables if t.id == order.table_id),
                None,
            )
            if table:
                table.is_occupied = False
                print(f"Столик {table.id} освобождён")

        print(f"Заказ #{order.id} завершён!")

    except ValueError:
        print("Неверный ввод!")
