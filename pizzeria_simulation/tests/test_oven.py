"""Tests for oven queue and baking behavior."""
from __future__ import annotations

from pizzeria.domain.models import Oven


def test_oven_moves_tasks_from_queue() -> None:
    """Ready task leaves oven and queued task starts baking."""
    oven = Oven(id=1, capacity=1)
    oven.enqueue_pizza(pizza_id=1, baking_minutes=10)
    oven.enqueue_pizza(pizza_id=2, baking_minutes=10)

    ready, moved = oven.tick(minutes=10)

    assert ready == [1]
    assert moved == [2]
    assert len(oven.baking) == 1
    assert oven.baking[0].pizza_id == 2
