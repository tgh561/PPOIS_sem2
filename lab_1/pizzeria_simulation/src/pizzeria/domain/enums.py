"""Domain enums for the pizzeria simulation."""
from __future__ import annotations

from enum import StrEnum


class CustomerType(StrEnum):
    """Types of customers."""

    DINE_IN = "dine_in"
    DELIVERY = "delivery"


class EmployeeRole(StrEnum):
    """Supported employee roles."""

    COOK = "cook"
    COURIER = "courier"
    CASHIER = "cashier"
    MANAGER = "manager"


class OrderStatus(StrEnum):
    """Lifecycle statuses for orders."""

    CREATED = "created"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    BAKING = "baking"
    READY = "ready"
    OUT_FOR_DELIVERY = "out_for_delivery"
    COMPLETED = "completed"
    CANCELED = "canceled"


class PizzaStatus(StrEnum):
    """Lifecycle statuses for a pizza."""

    CREATED = "created"
    PREPARING = "preparing"
    BAKING = "baking"
    READY = "ready"


class PizzaSize(StrEnum):
    """Pizza size options."""

    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class PaymentType(StrEnum):
    """Supported payment methods."""

    CASH = "cash"
    CARD = "card"
