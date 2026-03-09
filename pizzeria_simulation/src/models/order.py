"""Orders module."""
from dataclasses import dataclass, field

from src.enums import OrderType, OrderStatus


@dataclass
class OrderItem:
    """Order line item."""
    id: int
    menu_item_id: int
    quantity: int
    unit_price: float
    total_price: float


@dataclass
class Order:
    """Customer order."""
    id: int
    type: OrderType
    customer_phone: str | None
    table_id: int | None
    delivery_address: str | None
    items: list[OrderItem]
    status: OrderStatus
    created_at: str
    estimated_ready_time: str | None
    total_price: float
    tips_amount: float
    delivery_started_at: str | None = None
    delivery_ticks: int = 0
