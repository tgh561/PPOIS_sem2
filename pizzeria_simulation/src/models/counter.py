"""Стойка заказов, меню и касса."""
from dataclasses import dataclass


@dataclass
class MenuItem:
    """Позиция меню."""
    id: int
    name: str
    price: float
    is_available: bool
    category: str


@dataclass
class Menu:
    """Меню пиццерии."""
    items: list[MenuItem]
    pizza_bases: list[PizzaBaseItem] | None = None
    toppings: list[Topping] | None = None


@dataclass
class CashRegister:
    """Кассовый аппарат."""
    id: int
    cash_amount: float
    has_receipt_paper: bool


@dataclass
class CardTerminal:
    """Платёжный терминал."""
    id: int
    is_working: bool
    is_online: bool
    has_receipt_paper: bool


@dataclass
class OrderDesk:
    """Стойка заказов."""
    menu: Menu
    cash_register: CashRegister
    card_terminal: CardTerminal
    phone_number: str
