"""Payment models."""
from __future__ import annotations

from dataclasses import dataclass

from pizzeria.domain import PaymentType
from pizzeria.domain.exceptions import PaymentError


@dataclass(slots=True)
class CardTerminal:
    """Card terminal model."""

    is_operational: bool = True
    is_connected: bool = True
    has_receipt_paper: bool = True

    def can_process(self) -> bool:
        """Check if terminal can process card payments."""
        return self.is_operational and self.is_connected and self.has_receipt_paper

    def to_dict(self) -> dict:
        """Serialize terminal."""
        return {
            "is_operational": self.is_operational,
            "is_connected": self.is_connected,
            "has_receipt_paper": self.has_receipt_paper,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CardTerminal":
        """Deserialize terminal."""
        return cls(
            is_operational=bool(data.get("is_operational", True)),
            is_connected=bool(data.get("is_connected", True)),
            has_receipt_paper=bool(data.get("has_receipt_paper", True)),
        )


@dataclass(slots=True)
class CashDesk:
    """Cash desk model."""

    cash_amount: float = 0.0
    has_receipt_paper: bool = True

    def to_dict(self) -> dict:
        """Serialize cash desk."""
        return {
            "cash_amount": self.cash_amount,
            "has_receipt_paper": self.has_receipt_paper,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CashDesk":
        """Deserialize cash desk."""
        return cls(
            cash_amount=float(data.get("cash_amount", 0.0)),
            has_receipt_paper=bool(data.get("has_receipt_paper", True)),
        )


@dataclass(slots=True)
class PaymentSystem:
    """Payment processing aggregate."""

    card_terminal: CardTerminal
    cash_desk: CashDesk

    def process(self, amount: float, payment_type: PaymentType) -> None:
        """Process payment using selected method."""
        if amount <= 0:
            raise PaymentError("Сумма оплаты должна быть больше нуля")

        if payment_type == PaymentType.CARD:
            if not self.card_terminal.can_process():
                raise PaymentError("Терминал недоступен для оплаты картой")
            return

        if payment_type == PaymentType.CASH:
            if not self.cash_desk.has_receipt_paper:
                raise PaymentError("В кассе закончилась чековая лента")
            self.cash_desk.cash_amount = round(self.cash_desk.cash_amount + amount, 2)
            return

        raise PaymentError("Неподдерживаемый способ оплаты")

    def to_dict(self) -> dict:
        """Serialize payment system."""
        return {
            "card_terminal": self.card_terminal.to_dict(),
            "cash_desk": self.cash_desk.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PaymentSystem":
        """Deserialize payment system."""
        return cls(
            card_terminal=CardTerminal.from_dict(data.get("card_terminal", {})),
            cash_desk=CashDesk.from_dict(data.get("cash_desk", {})),
        )
