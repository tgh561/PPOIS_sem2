"""Integration tests for pizzeria flow."""
from __future__ import annotations

from pathlib import Path

import pytest

from pizzeria.domain import OrderStatus, PaymentType, PizzaSize
from pizzeria.domain.models import create_default_pizzeria
from pizzeria.infrastructure.persistence import JsonStateRepository


def test_delivery_order_full_flow() -> None:
    """Delivery order should pass full lifecycle and end as completed."""
    pizzeria = create_default_pizzeria()
    order = pizzeria.create_delivery_order(
        delivery_address="Main st. 1",
        delivery_phone="+1000000",
        pizza_item_ids=[1],
        size=PizzaSize.MEDIUM,
        payment_type=PaymentType.CARD,
    )

    pizzeria.confirm_order(order.id)
    pizzeria.send_order_to_kitchen(order.id)
    for _ in range(3):
        pizzeria.tick_kitchen(minutes=10)

    pizzeria.start_delivery(order.id)
    for _ in range(3):
        pizzeria.tick_delivery(minutes=10)

    pizzeria.pay_order(order.id)
    completed = pizzeria.complete_order(order.id)

    assert completed.is_paid is True
    assert completed.status == OrderStatus.COMPLETED


def test_json_repository_roundtrip(tmp_path: Path) -> None:
    """Roundtrip through repository should keep order data."""
    pizzeria = create_default_pizzeria()
    order = pizzeria.create_dine_in_order(
        table_number=1,
        guests_count=2,
        pizza_item_ids=[1, 2],
        drink_item_ids=[101],
        size=PizzaSize.SMALL,
        payment_type=PaymentType.CASH,
    )

    state_file = tmp_path / "state.json"
    repo = JsonStateRepository(filepath=state_file)
    repo.save(pizzeria)
    loaded = repo.load()

    loaded_order = next(item for item in loaded.orders if item.id == order.id)
    assert len(loaded_order.pizzas) == 2
    assert len(loaded_order.drinks) == 1
    assert loaded_order.table_number == 1


def test_order_can_include_drinks() -> None:
    """Order total should include drinks."""
    pizzeria = create_default_pizzeria()
    order = pizzeria.create_dine_in_order(
        table_number=1,
        guests_count=2,
        pizza_item_ids=[1],
        drink_item_ids=[101, 106],
        size=PizzaSize.MEDIUM,
        payment_type=PaymentType.CASH,
    )

    assert len(order.pizzas) == 1
    assert len(order.drinks) == 2
    assert order.total_price == pytest.approx(14.9)


def test_pay_order_with_tips(monkeypatch: pytest.MonkeyPatch) -> None:
    """Payment should include tips when random branch chooses it."""
    pizzeria = create_default_pizzeria()
    order = pizzeria.create_dine_in_order(
        table_number=1,
        guests_count=2,
        pizza_item_ids=[1],
        size=PizzaSize.MEDIUM,
        payment_type=PaymentType.CASH,
    )
    pizzeria.confirm_order(order.id)
    pizzeria.send_order_to_kitchen(order.id)
    pizzeria.tick_kitchen(minutes=20)

    monkeypatch.setattr("pizzeria.domain.models.pizzeria.random.random", lambda: 0.25)
    monkeypatch.setattr("pizzeria.domain.models.pizzeria.random.randint", lambda _a, _b: 15)

    paid = pizzeria.pay_order(order.id)

    assert paid.is_paid is True
    assert paid.tip_percent == 15
    assert paid.tip_amount == pytest.approx(1.43)
    assert paid.paid_amount == pytest.approx(10.93)
    assert pizzeria.tips_total == pytest.approx(1.43)


def test_pay_order_without_tips(monkeypatch: pytest.MonkeyPatch) -> None:
    """Payment should have zero tips when random branch skips tips."""
    pizzeria = create_default_pizzeria()
    order = pizzeria.create_dine_in_order(
        table_number=1,
        guests_count=2,
        pizza_item_ids=[1],
        size=PizzaSize.MEDIUM,
        payment_type=PaymentType.CASH,
    )
    pizzeria.confirm_order(order.id)
    pizzeria.send_order_to_kitchen(order.id)
    pizzeria.tick_kitchen(minutes=20)

    monkeypatch.setattr("pizzeria.domain.models.pizzeria.random.random", lambda: 0.75)
    paid = pizzeria.pay_order(order.id)

    assert paid.is_paid is True
    assert paid.tip_percent == 0
    assert paid.tip_amount == 0.0
    assert paid.paid_amount == pytest.approx(order.total_price)
    assert pizzeria.tips_total == 0.0


def test_large_order_needs_more_kitchen_ticks() -> None:
    """Order larger than oven capacity should take extra simulation ticks."""
    pizzeria = create_default_pizzeria()
    order = pizzeria.create_dine_in_order(
        table_number=1,
        guests_count=2,
        pizza_item_ids=[1, 1, 1, 1, 1, 1, 1, 1],
        size=PizzaSize.MEDIUM,
        payment_type=PaymentType.CARD,
    )

    pizzeria.confirm_order(order.id)
    pizzeria.send_order_to_kitchen(order.id)

    for _ in range(3):
        pizzeria.tick_kitchen(minutes=10)

    assert order.status != OrderStatus.READY

    pizzeria.tick_kitchen(minutes=10)
    assert order.status == OrderStatus.READY


def test_state_persistence_keeps_payment_and_tips(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Saved state should preserve payment flag, tips, totals and completion."""
    pizzeria = create_default_pizzeria()
    order = pizzeria.create_dine_in_order(
        table_number=1,
        guests_count=2,
        pizza_item_ids=[2],
        size=PizzaSize.MEDIUM,
        payment_type=PaymentType.CASH,
    )
    pizzeria.confirm_order(order.id)
    pizzeria.send_order_to_kitchen(order.id)
    pizzeria.tick_kitchen(minutes=20)

    monkeypatch.setattr("pizzeria.domain.models.pizzeria.random.random", lambda: 0.2)
    monkeypatch.setattr("pizzeria.domain.models.pizzeria.random.randint", lambda _a, _b: 12)
    pizzeria.pay_order(order.id)
    pizzeria.complete_order(order.id)

    state_file = tmp_path / "state.json"
    repo = JsonStateRepository(filepath=state_file)
    repo.save(pizzeria)
    loaded = repo.load()

    loaded_order = next(item for item in loaded.orders if item.id == order.id)
    assert loaded_order.status == OrderStatus.COMPLETED
    assert loaded_order.is_paid is True
    assert loaded_order.tip_percent == 12
    assert loaded_order.tip_amount == pytest.approx(1.32)
    assert loaded_order.paid_amount == pytest.approx(12.32)
    assert loaded.revenue == pytest.approx(11.0)
    assert loaded.tips_total == pytest.approx(1.32)
    assert loaded.hall.find_table(1).is_occupied is False


def test_state_persistence_keeps_active_delivery_task(tmp_path: Path) -> None:
    """Saved state should preserve active delivery task and remaining minutes."""
    pizzeria = create_default_pizzeria()
    order = pizzeria.create_delivery_order(
        delivery_address="Lenina 10",
        delivery_phone="+375000000",
        pizza_item_ids=[1],
        size=PizzaSize.MEDIUM,
        payment_type=PaymentType.CARD,
    )
    pizzeria.confirm_order(order.id)
    pizzeria.send_order_to_kitchen(order.id)
    pizzeria.tick_kitchen(minutes=20)
    pizzeria.start_delivery(order.id)
    pizzeria.tick_delivery(minutes=10)

    state_file = tmp_path / "state.json"
    repo = JsonStateRepository(filepath=state_file)
    repo.save(pizzeria)
    loaded = repo.load()

    loaded_order = next(item for item in loaded.orders if item.id == order.id)
    assert loaded_order.status == OrderStatus.OUT_FOR_DELIVERY
    assert loaded_order.is_paid is False
    assert loaded.delivery.is_in_progress(order.id) is True
    assert loaded.delivery.tasks[order.id].remaining_minutes == 20
