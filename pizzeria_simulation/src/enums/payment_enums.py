"""Методы оплаты."""
from enum import StrEnum


class PaymentMethod(StrEnum):
    """Методы оплаты."""
    CASH = "cash"
    CARD = "card"
