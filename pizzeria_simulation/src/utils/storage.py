"""Сохранение и загрузка состояния."""
import json
from pathlib import Path
from dataclasses import asdict

from src.models import PizzeriaState, create_default_state


STATE_FILE = Path("data/state.json")


def _convert_value(value):
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, list):
        return [_convert_value(v) for v in value]
    if isinstance(value, dict):
        return {k: _convert_value(v) for k, v in value.items()}
    return value


def state_to_dict(state: PizzeriaState) -> dict:
    data = asdict(state)
    return _convert_value(data)


def dict_to_state(data: dict) -> PizzeriaState:
    state = create_default_state()

    state.next_id = data.get("next_id", 1)
    state.finance.total_revenue = data.get("finance", {}).get("total_revenue", 0.0)
    state.finance.total_tips = data.get("finance", {}).get("total_tips", 0.0)

    orders_data = data.get("orders", [])
    state.orders = _restore_orders(orders_data)

    payments_data = data.get("payments", [])
    if isinstance(payments_data, str):
        payments_data = []
    state.payments = _restore_payments(payments_data)

    state.dining_hall = _restore_dining_hall(data.get("dining_hall", {}))
    state.staff_team = _restore_staff_team(data.get("staff_team", {}))
    state.kitchen = _restore_kitchen(data.get("kitchen", {}))

    return state


def _restore_orders(orders_data: list) -> list:
    from src.models import Order, OrderItem
    from src.enums import OrderType, OrderStatus

    orders = []
    for order_data in orders_data:
        items_data = order_data.get("items", [])
        items = [
            OrderItem(
                id=item["id"],
                menu_item_id=item["menu_item_id"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                total_price=item["total_price"],
            )
            for item in items_data
        ]

        order = Order(
            id=order_data["id"],
            type=OrderType(order_data["type"]),
            customer_phone=order_data.get("customer_phone"),
            table_id=order_data.get("table_id"),
            delivery_address=order_data.get("delivery_address"),
            items=items,
            status=OrderStatus(order_data["status"]),
            created_at=order_data["created_at"],
            estimated_ready_time=order_data.get("estimated_ready_time"),
            total_price=order_data["total_price"],
            tips_amount=order_data.get("tips_amount", 0.0),
            delivery_started_at=order_data.get("delivery_started_at"),
            delivery_ticks=order_data.get("delivery_ticks", 0),
        )
        orders.append(order)

    return orders


def _restore_payments(payments_data: list) -> list:
    from src.models import Payment
    from src.enums import PaymentMethod

    payments = []
    for payment_data in payments_data:
        payment = Payment(
            id=payment_data["id"],
            order_id=payment_data["order_id"],
            amount=payment_data["amount"],
            method=PaymentMethod(payment_data["method"]),
            paid_at=payment_data["paid_at"],
            success=payment_data["success"],
        )
        payments.append(payment)

    return payments


def _restore_dining_hall(data: dict) -> "DiningHall":
    from src.models import DiningHall, Table

    tables_data = data.get("tables", [])
    tables = [
        Table(
            id=t["id"],
            capacity=t["capacity"],
            is_occupied=t["is_occupied"],
        )
        for t in tables_data
    ]
    return DiningHall(tables)


def _restore_staff_team(data: dict) -> "StaffTeam":
    from src.models import StaffTeam, Employee
    from src.enums import EmployeeRole

    employees_data = data.get("employees", [])
    employees = [
        Employee(
            id=e["id"],
            name=e["name"],
            role=EmployeeRole(e["role"]),
            base_salary=e["base_salary"],
            tips=e.get("tips", 0.0),
        )
        for e in employees_data
    ]
    return StaffTeam(employees)


def _restore_kitchen(data: dict) -> "Kitchen":
    from src.models import Kitchen

    return Kitchen(
        orders_in_queue=data.get("orders_in_queue", []),
        orders_cooking=data.get("orders_cooking", []),
        orders_baked=data.get("orders_baked", []),
    )


def load_state() -> PizzeriaState:
    if not STATE_FILE.exists():
        print("Файл состояния не найден, создаём новое")
        return create_default_state()

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        state = dict_to_state(data)
        print("Состояние загружено из файла")
        return state

    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Ошибка загрузки состояния: {e}")
        return create_default_state()


def save_state(state: PizzeriaState) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    data = state_to_dict(state)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Сохранено в {STATE_FILE}")
    print(f"{len(state.orders)} заказов, {len(state.payments)} оплат")


from enum import Enum
