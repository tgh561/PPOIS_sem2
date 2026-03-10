"""Customer domain models."""
from __future__ import annotations

from dataclasses import dataclass

from pizzeria.domain import CustomerType


@dataclass(slots=True)
class Customer:
    """Base customer abstraction."""

    id: int
    customer_type: CustomerType


@dataclass(slots=True)
class DineInCustomer(Customer):
    """Customer eating in dining hall."""

    table_number: int
    guests_count: int

    def __init__(self, customer_id: int, table_number: int, guests_count: int) -> None:
        super().__init__(id=customer_id, customer_type=CustomerType.DINE_IN)
        self.table_number = table_number
        self.guests_count = guests_count


@dataclass(slots=True)
class DeliveryCustomer(Customer):
    """Customer for delivery orders."""

    address: str
    phone: str

    def __init__(self, customer_id: int, address: str, phone: str) -> None:
        super().__init__(id=customer_id, customer_type=CustomerType.DELIVERY)
        self.address = address
        self.phone = phone
