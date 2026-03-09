"""Платежи."""
from dataclasses import dataclass

from src.enums import PaymentMethod


@dataclass
class Payment:
    """Платёж."""
    id: int
    order_id: int
    amount: float
    method: PaymentMethod
    paid_at: str
    success: bool
