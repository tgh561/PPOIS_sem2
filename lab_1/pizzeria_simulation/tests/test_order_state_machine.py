"""Tests for order lifecycle transitions."""
from __future__ import annotations

import pytest

from pizzeria.domain import CustomerType, InvalidStateTransitionError, OrderStatus, PaymentType, PizzaSize
from pizzeria.domain.models import Order, Pizza


def test_valid_transitions() -> None:
    """Order should pass allowed lifecycle transitions."""
    pizza = Pizza(
        id=1,
        name="Margherita",
        size=PizzaSize.MEDIUM,
        toppings=["mozzarella"],
        ingredient_requirements={"dough": 1.0},
        base_price=10.0,
    )
    order = Order.new(
        order_id=1,
        pizzas=[pizza],
        customer_type=CustomerType.DINE_IN,
        payment_type=PaymentType.CASH,
        table_number=1,
    )

    order.confirm()
    order.start_preparing()
    order.start_baking()
    order.mark_ready()
    order.complete()

    assert order.status == OrderStatus.COMPLETED


def test_invalid_transition_raises() -> None:
    """Invalid state transition should raise domain error."""
    pizza = Pizza(
        id=1,
        name="Pepperoni",
        size=PizzaSize.MEDIUM,
        toppings=["pepperoni"],
        ingredient_requirements={"dough": 1.0},
        base_price=10.0,
    )
    order = Order.new(
        order_id=10,
        pizzas=[pizza],
        customer_type=CustomerType.DINE_IN,
        payment_type=PaymentType.CARD,
        table_number=2,
    )

    with pytest.raises(InvalidStateTransitionError):
        order.mark_ready()
