"""Kitchen management commands."""
import random

from src.models import PizzeriaState, OrderStatus, OrderType


def print_kitchen_menu() -> None:
    print("\n" + "=" * 40)
    print("КУХНЯ")
    print("=" * 40)
    print("1. Взять заказ из очереди на готовку")
    print("2. Симулировать 10 минут (приготовление)")
    print("3. Симулировать доставку (1 тик)")
    print("4. Заказы в очереди")
    print("5. Заказы в готовке")
    print("6. Готовые заказы")
    print("0. Назад")
    print("=" * 40)


def handle_kitchen_menu(state: PizzeriaState) -> None:
    while True:
        print_kitchen_menu()
        print(f"В очереди: {len(state.kitchen.orders_in_queue)}")
        print(f"В готовке: {len(state.kitchen.orders_cooking)}")
        print(f"Готово: {len(state.kitchen.orders_baked)}")
        
        delivery_orders = [
            o for o in state.orders
            if o.status == OrderStatus.OUT_FOR_DELIVERY and o.delivery_ticks < 3
        ]
        if delivery_orders:
            print(f"\nВ доставке: {len(delivery_orders)}")
            for o in delivery_orders:
                print(f"  Заказ #{o.id} — тик {o.delivery_ticks}/3")

        choice = input("Выберите действие: ").strip()

        if choice == "0":
            break
        elif choice == "1":
            take_next_order_to_cooking(state)
        elif choice == "2":
            simulate_cooking_time(state, minutes=10)
        elif choice == "3":
            simulate_delivery_tick(state)
        elif choice == "4":
            show_orders_in_queue(state)
        elif choice == "5":
            show_orders_cooking(state)
        elif choice == "6":
            show_orders_baked(state)
        else:
            print("Неверный выбор!")


def take_next_order_to_cooking(state: PizzeriaState) -> None:
    ready_orders = [
        o for o in state.orders
        if o.status == OrderStatus.CREATED
        and o.id not in state.kitchen.orders_in_queue
        and o.id not in state.kitchen.orders_cooking
        and o.id not in state.kitchen.orders_baked
    ]

    if not ready_orders:
        print("Нет заказов для готовки")
        return

    print("\nДОСТУПНЫЕ ЗАКАЗЫ:")
    for order in ready_orders:
        type_str = "На месте" if order.type == OrderType.ON_SITE else "Доставка"
        table_info = f"Столик {order.table_id}" if order.table_id else f"Адрес: {order.delivery_address}"
        print(f"#{order.id} | {type_str} | {table_info} | {order.total_price:.2f}р")

    try:
        order_id = int(input("ID заказа для готовки (0 для первого): "))
        
        if order_id == 0:
            order_id = ready_orders[0].id
        
        order = next((o for o in ready_orders if o.id == order_id), None)
        if not order:
            print("Заказ не найден!")
            return

        if order_id not in state.kitchen.orders_in_queue:
            state.kitchen.orders_in_queue.append(order_id)
            order.status = OrderStatus.IN_QUEUE
            print(f"Заказ #{order_id} добавлен в очередь на кухню")
        else:
            print("Заказ уже в очереди")

    except ValueError:
        print("Неверный ввод!")


def simulate_cooking_time(state: PizzeriaState, minutes: int) -> None:
    print(f"\nПрошло {minutes} минут (приготовление)...")
    progressed = 0

    if state.kitchen.orders_in_queue:
        moved_to_cooking = state.kitchen.orders_in_queue.pop(0)
        state.kitchen.orders_cooking.append(moved_to_cooking)
        
        order = next((o for o in state.orders if o.id == moved_to_cooking), None)
        if order:
            order.status = OrderStatus.COOKING
        
        progressed += 1
        print(f"Заказ #{moved_to_cooking} начал готовиться")

    if state.kitchen.orders_cooking and random.random() < 0.8:
        moved_to_baked = state.kitchen.orders_cooking.pop(0)
        state.kitchen.orders_baked.append(moved_to_baked)
        
        order = next((o for o in state.orders if o.id == moved_to_baked), None)
        if order:
            order.status = OrderStatus.READY
        
        progressed += 1
        print(f"Заказ #{moved_to_baked} готов!")

    if progressed == 0:
        print("Ничего не изменилось")

    print(f"В очереди: {len(state.kitchen.orders_in_queue)} | В готовке: {len(state.kitchen.orders_cooking)} | Готово: {len(state.kitchen.orders_baked)}")


def simulate_delivery_tick(state: PizzeriaState) -> None:
    delivery_orders = [
        o for o in state.orders
        if o.status == OrderStatus.OUT_FOR_DELIVERY and o.delivery_ticks < 3
    ]

    if not delivery_orders:
        print("Нет активных доставок")
        return

    print("\nСимуляция доставки (10 минут)...")
    
    for order in delivery_orders:
        order.delivery_ticks += 1
        print(f"Заказ #{order.id}: тик {order.delivery_ticks}/3")
        
        if order.delivery_ticks >= 3:
            print(f"Заказ #{order.id} прибыл к клиенту! Требуется оплата.")


def show_orders_in_queue(state: PizzeriaState) -> None:
    if not state.kitchen.orders_in_queue:
        print("Очередь пуста")
        return

    print("\nЗАКАЗЫ В ОЧЕРЕДИ:")
    for order_id in state.kitchen.orders_in_queue:
        order = next((o for o in state.orders if o.id == order_id), None)
        if order:
            print(f"#{order.id} | {order.total_price:.1f}р")


def show_orders_cooking(state: PizzeriaState) -> None:
    if not state.kitchen.orders_cooking:
        print("Ничего не готовится")
        return

    print("\nЗАКАЗЫ В ГОТОВКЕ:")
    for order_id in state.kitchen.orders_cooking:
        order = next((o for o in state.orders if o.id == order_id), None)
        if order:
            print(f"#{order.id} | {order.total_price:.1f}р")


def show_orders_baked(state: PizzeriaState) -> None:
    if not state.kitchen.orders_baked:
        print("Нет готовых заказов")
        return

    print("\nГОТОВЫЕ ЗАКАЗЫ:")
    for order_id in state.kitchen.orders_baked:
        order = next((o for o in state.orders if o.id == order_id), None)
        if order:
            type_str = "На месте" if order.type == OrderType.ON_SITE else "Доставка"
            table_info = f"Столик {order.table_id}" if order.table_id else f"Адрес: {order.delivery_address}"
            print(f"#{order.id} | {type_str} | {table_info} | {order.total_price:.1f}р")
