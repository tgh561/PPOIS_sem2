"""Order types and statuses."""
from enum import StrEnum


class OrderType(StrEnum):
    """Order types."""
    ON_SITE = "on_site"
    DELIVERY = "delivery"


class OrderStatus(StrEnum):
    """Order statuses matching the workflow."""
    CREATED = "created"
    IN_QUEUE = "in_queue"
    COOKING = "cooking"
    READY = "ready"
    SERVED = "served"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERING = "delivering"
    PAID = "paid"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
