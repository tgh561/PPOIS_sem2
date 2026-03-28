"""Domain package for pizzeria simulation."""

from .enums import (
    CustomerType,
    EmployeeRole,
    OrderStatus,
    PaymentType,
    PizzaSize,
    PizzaStatus,
)
from .exceptions import (
    DomainError,
    InvalidStateTransitionError,
    NotFoundError,
    PaymentError,
    ResourceUnavailableError,
    ValidationError,
)

__all__ = [
    "CustomerType",
    "EmployeeRole",
    "OrderStatus",
    "PaymentType",
    "PizzaSize",
    "PizzaStatus",
    "DomainError",
    "InvalidStateTransitionError",
    "NotFoundError",
    "PaymentError",
    "ResourceUnavailableError",
    "ValidationError",
]
