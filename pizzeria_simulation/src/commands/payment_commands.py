"""Payment management commands."""
import random

from src.models import PizzeriaState, OrderStatus, Payment, PaymentMethod, OrderType


def print_payments_menu() -> None:
    print("\n" + "=" * 40)
    print("ОПЛАТЫ")
    print("=" * 40)
    print("1. Оплатить наличными")
    print("2. Оплатить картой")
    print("3. Добавить чаевые")
    print("4. История оплат")
    print("5. Финансовый отчёт")
    print("0. Назад")
    print("=" * 40)


def handle_payments_menu(state: PizzeriaState) -> None:
    while True:
        print_payments_menu()
        print(f"В кассе: {state.order_desk.cash_register.cash_amount:.2f}р")
        print(f"Выручка: {state.finance.total_revenue:.2f}р")
        print(f"Чаевые: {state.finance.total_tips:.2f}р")
        terminal_status = "онлайн" if state.order_desk.card_terminal.is_online else "оффлайн"
        print(f"Терминал: {terminal_status}")

        choice = input("Выберите действие: ").strip()

        if choice == "0":
            break
        elif choice == "1":
            process_cash_payment(state)
        elif choice == "2":
            process_card_payment(state)
        elif choice == "3":
            add_tips(state)
        elif choice == "4":
            show_payment_history(state)
        elif choice == "5":
            show_finance_report(state)
        else:
            print("Неверный выбор!")


def process_cash_payment(state: PizzeriaState) -> None:
    unpaid_orders = [
        o for o in state.orders 
        if o.status in (OrderStatus.SERVED, OrderStatus.OUT_FOR_DELIVERY, OrderStatus.DELIVERING)
    ]

    if not unpaid_orders:
        print("Нет неоплаченных заказов!")
        return

    print("\nНЕОПЛАЧЕННЫЕ ЗАКАЗЫ:")
    for order in unpaid_orders:
        type_str = "На месте" if order.type == OrderType.ON_SITE else "Доставка"
        table_info = f"Столик {order.table_id}" if order.table_id else f"Адрес: {order.delivery_address}"
        print(f"#{order.id} | {type_str} | {table_info} | {order.status.value} | {order.total_price:.2f}р")

    try:
        order_id = int(input("ID заказа для оплаты (0 для отмены): "))
        if order_id == 0:
            return
            
        order = next((o for o in unpaid_orders if o.id == order_id), None)

        if not order:
            print("Заказ не найден!")
            return

        if not state.order_desk.cash_register.has_receipt_paper:
            print("Нет бумаги для чека!")
            return

        print(f"\nСумма к оплате: {order.total_price:.2f}р")
        tips_input = input("Чаевые (Enter=0): ").strip()
        tips_amount = float(tips_input) if tips_input else 0.0

        total_payment = order.total_price + tips_amount

        payment = Payment(
            id=state.next_id,
            order_id=order.id,
            amount=order.total_price,
            method=PaymentMethod.CASH,
            paid_at="2026-03-09T21:00:00",
            success=True
        )
        state.payments.append(payment)
        state.next_id += 1

        state.order_desk.cash_register.cash_amount += total_payment
        order.status = OrderStatus.PAID
        state.finance.total_revenue += order.total_price
        
        if tips_amount > 0:
            state.finance.total_tips += tips_amount
            distribute_tips(state, tips_amount)
            print(f"Чаевые {tips_amount:.2f}р добавлены!")

        print(f"Оплата #{payment.id} прошла успешно!")
        print(f"В кассе: {state.order_desk.cash_register.cash_amount:.2f}р")

        if order.type == OrderType.DELIVERY and order.delivery_ticks >= 3:
            print("Заказ доставлен и оплачен — готов к завершению!")

    except ValueError:
        print("Неверный ввод!")


def process_card_payment(state: PizzeriaState) -> None:
    if not state.order_desk.card_terminal.is_working:
        print("Терминал не работает!")
        return

    if not state.order_desk.card_terminal.is_online:
        print("Нет связи с банком!")
        return

    if not state.order_desk.card_terminal.has_receipt_paper:
        print("Нет бумаги для чека!")
        return

    unpaid_orders = [
        o for o in state.orders 
        if o.status in (OrderStatus.SERVED, OrderStatus.OUT_FOR_DELIVERY, OrderStatus.DELIVERING)
    ]

    if not unpaid_orders:
        print("Нет неоплаченных заказов!")
        return

    print("\nНЕОПЛАЧЕННЫЕ ЗАКАЗЫ:")
    for order in unpaid_orders:
        type_str = "На месте" if order.type == OrderType.ON_SITE else "Доставка"
        table_info = f"Столик {order.table_id}" if order.table_id else f"Адрес: {order.delivery_address}"
        print(f"#{order.id} | {type_str} | {table_info} | {order.status.value} | {order.total_price:.2f}р")

    try:
        order_id = int(input("ID заказа для оплаты (0 для отмены): "))
        if order_id == 0:
            return
            
        order = next((o for o in unpaid_orders if o.id == order_id), None)

        if not order:
            print("Заказ не найден!")
            return

        print(f"\nСумма к оплате: {order.total_price:.2f}р")
        tips_input = input("Чаевые (Enter=0): ").strip()
        tips_amount = float(tips_input) if tips_input else 0.0

        if random.random() < 0.9:
            payment = Payment(
                id=state.next_id,
                order_id=order.id,
                amount=order.total_price,
                method=PaymentMethod.CARD,
                paid_at="2026-03-09T21:00:00",
                success=True
            )
            state.payments.append(payment)
            state.next_id += 1

            order.status = OrderStatus.PAID
            state.finance.total_revenue += order.total_price
            
            if tips_amount > 0:
                state.finance.total_tips += tips_amount
                distribute_tips(state, tips_amount)
                print(f"Чаевые {tips_amount:.2f}р добавлены!")
                
            print(f"Карта принята! Заказ #{order.id} оплачен.")

            if order.type == OrderType.DELIVERY and order.delivery_ticks >= 3:
                print("Заказ доставлен и оплачен — готов к завершению!")
        else:
            print("Ошибка авторизации карты!")

    except ValueError:
        print("Неверный ввод!")


def distribute_tips(state: PizzeriaState, tips_amount: float) -> None:
    cooks = [e for e in state.staff_team.employees if e.role.value == "cook"]
    waiters = [e for e in state.staff_team.employees if e.role.value == "waiter"]
    couriers = [e for e in state.staff_team.employees if e.role.value == "courier"]
    
    cook_share = tips_amount * 0.5
    waiter_share = tips_amount * 0.3
    courier_share = tips_amount * 0.2
    
    if cooks:
        per_cook = cook_share / len(cooks)
        for cook in cooks:
            cook.tips += per_cook
    
    if waiters:
        per_waiter = waiter_share / len(waiters)
        for waiter in waiters:
            waiter.tips += per_waiter
    
    if couriers:
        per_courier = courier_share / len(couriers)
        for courier in couriers:
            courier.tips += per_courier


def add_tips(state: PizzeriaState) -> None:
    print("\nСОТРУДНИКИ:")
    for emp in state.staff_team.employees:
        print(f"{emp.id}. {emp.name} ({emp.role.value}) — чаевые: {emp.tips:.2f}р")

    try:
        emp_id = int(input("\nID сотрудника (0 для отмены): "))
        if emp_id == 0:
            return
            
        employee = next((e for e in state.staff_team.employees if e.id == emp_id), None)
        if not employee:
            print("Сотрудник не найден!")
            return

        tips_input = input("Сумма чаевых: ").strip()
        tips_amount = float(tips_input) if tips_input else 0.0

        if tips_amount <= 0:
            print("Сумма должна быть больше 0!")
            return

        employee.tips += tips_amount
        state.finance.total_tips += tips_amount
        state.order_desk.cash_register.cash_amount -= tips_amount

        print(f"Чаевые {tips_amount:.2f}р добавлены {employee.name}!")

    except ValueError:
        print("Неверный ввод!")


def show_payment_history(state: PizzeriaState) -> None:
    if not state.payments:
        print("Оплат пока нет")
        return

    print("\nИСТОРИЯ ОПЛАТ:")
    total_today = sum(p.amount for p in state.payments)
    total_tips = state.finance.total_tips
    print(f"Всего оплат: {len(state.payments)} | Сумма: {total_today:.2f}р | Чаевые: {total_tips:.2f}р")

    for payment in state.payments[-10:]:
        method = "Наличные" if payment.method == PaymentMethod.CASH else "Карта"
        status = "OK" if payment.success else "FAIL"
        print(f"{status} #{payment.id} | {method} | {payment.amount:.2f}р | Заказ #{payment.order_id}")


def show_finance_report(state: PizzeriaState) -> None:
    print("\nФИНАНСОВЫЙ ОТЧЁТ")
    print("=" * 40)
    print(f"Выручка всего: {state.finance.total_revenue:.2f}р")
    print(f"Чаевые всего: {state.finance.total_tips:.2f}р")
    print(f"В кассе: {state.order_desk.cash_register.cash_amount:.2f}р")
    
    total_salary = sum(e.base_salary for e in state.staff_team.employees)
    print(f"Зарплаты сотрудников: {total_salary:.2f}р")
    
    profit = state.finance.total_revenue - total_salary
    print(f"Прибыль (без учёта расходов): {profit:.2f}р")
    print("=" * 40)
