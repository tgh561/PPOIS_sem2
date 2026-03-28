"""Order domain model."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from pizzeria.domain import CustomerType, OrderStatus, PaymentType
from pizzeria.domain.exceptions import InvalidStateTransitionError, ValidationError
from pizzeria.domain.models.menu import MenuItem
from pizzeria.domain.models.pizza import Pizza

ALLOWED_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.CREATED: {OrderStatus.CONFIRMED, OrderStatus.CANCELED},
    OrderStatus.CONFIRMED: {OrderStatus.PREPARING, OrderStatus.CANCELED},
    OrderStatus.PREPARING: {OrderStatus.BAKING, OrderStatus.CANCELED},
    OrderStatus.BAKING: {OrderStatus.READY, OrderStatus.CANCELED},
    OrderStatus.READY: {OrderStatus.OUT_FOR_DELIVERY, OrderStatus.COMPLETED, OrderStatus.CANCELED},
    OrderStatus.OUT_FOR_DELIVERY: {OrderStatus.COMPLETED, OrderStatus.CANCELED},
    OrderStatus.COMPLETED: set(),
    OrderStatus.CANCELED: set(),
}

ORDER_STATUS_RU: dict[OrderStatus, str] = {
    OrderStatus.CREATED: "создан",
    OrderStatus.CONFIRMED: "подтверждён",
    OrderStatus.PREPARING: "подготовка",
    OrderStatus.BAKING: "выпекается",
    OrderStatus.READY: "готов",
    OrderStatus.OUT_FOR_DELIVERY: "в доставке",
    OrderStatus.COMPLETED: "выполнен",
    OrderStatus.CANCELED: "отменён",
}


@dataclass(slots=True)
class Order:
    """Main business entity of the pizzeria."""

    id: int
    pizzas: list[Pizza]
    status: OrderStatus
    customer_type: CustomerType
    table_number: int | None
    delivery_address: str | None
    delivery_phone: str | None
    payment_type: PaymentType
    total_price: float
    creation_time: str
    assigned_cook: int | None = None
    assigned_courier: int | None = None
    is_paid: bool = False
    drinks: list[MenuItem] = field(default_factory=list)
    tip_percent: int = 0
    tip_amount: float = 0.0
    paid_amount: float = 0.0

    def __post_init__(self) -> None:
        """Validate required fields."""
        if self.customer_type == CustomerType.DINE_IN and self.table_number is None:
            raise ValidationError("Для заказа в зале нужно указать номер столика")
        if self.customer_type == CustomerType.DELIVERY:
            if not self.delivery_address or not self.delivery_phone:
                raise ValidationError("Для заказа на доставку нужны адрес и телефон")

    def transition_to(self, target_status: OrderStatus) -> None:
        """Move order to next state with validation."""
        allowed = ALLOWED_TRANSITIONS[self.status]
        if target_status not in allowed:
            source_status = ORDER_STATUS_RU.get(self.status, self.status.value)
            destination_status = ORDER_STATUS_RU.get(target_status, target_status.value)
            raise InvalidStateTransitionError(
                f"Заказ {self.id}: переход из статуса '{source_status}' в '{destination_status}' недопустим"
            )
        self.status = target_status

    def confirm(self) -> None:
        """Confirm order."""
        self.transition_to(OrderStatus.CONFIRMED)

    def start_preparing(self) -> None:
        """Set order to preparing."""
        self.transition_to(OrderStatus.PREPARING)

    def start_baking(self) -> None:
        """Set order to baking."""
        self.transition_to(OrderStatus.BAKING)

    def mark_ready(self) -> None:
        """Mark order as ready."""
        self.transition_to(OrderStatus.READY)

    def send_out_for_delivery(self) -> None:
        """Mark order as out for delivery."""
        self.transition_to(OrderStatus.OUT_FOR_DELIVERY)

    def complete(self) -> None:
        """Mark order as completed."""
        self.transition_to(OrderStatus.COMPLETED)

    def cancel(self) -> None:
        """Cancel order."""
        self.transition_to(OrderStatus.CANCELED)

    def recalculate_total(self) -> float:
        """Recalculate order total based on pizzas and drinks."""
        pizzas_total = sum(pizza.price for pizza in self.pizzas)
        drinks_total = sum(drink.price for drink in self.drinks)
        self.total_price = round(pizzas_total + drinks_total, 2)
        return self.total_price

    def to_dict(self) -> dict:
        """Serialize order."""
        return {
            "id": self.id,
            "pizzas": [pizza.to_dict() for pizza in self.pizzas],
            "drinks": [drink.to_dict() for drink in self.drinks],
            "status": self.status.value,
            "customer_type": self.customer_type.value,
            "table_number": self.table_number,
            "delivery_address": self.delivery_address,
            "delivery_phone": self.delivery_phone,
            "payment_type": self.payment_type.value,
            "total_price": self.total_price,
            "creation_time": self.creation_time,
            "assigned_cook": self.assigned_cook,
            "assigned_courier": self.assigned_courier,
            "is_paid": self.is_paid,
            "tip_percent": self.tip_percent,
            "tip_amount": self.tip_amount,
            "paid_amount": self.paid_amount,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Order":
        """Deserialize order."""
        pizzas = [Pizza.from_dict(item) for item in data.get("pizzas", [])]
        drinks = [MenuItem.from_dict(item) for item in data.get("drinks", [])]
        return cls(
            id=int(data["id"]),
            pizzas=pizzas,
            drinks=drinks,
            status=OrderStatus(data["status"]),
            customer_type=CustomerType(data["customer_type"]),
            table_number=data.get("table_number"),
            delivery_address=data.get("delivery_address"),
            delivery_phone=data.get("delivery_phone"),
            payment_type=PaymentType(data["payment_type"]),
            total_price=float(data["total_price"]),
            creation_time=str(data["creation_time"]),
            assigned_cook=data.get("assigned_cook"),
            assigned_courier=data.get("assigned_courier"),
            is_paid=bool(data.get("is_paid", False)),
            tip_percent=int(data.get("tip_percent", 0)),
            tip_amount=float(data.get("tip_amount", 0.0)),
            paid_amount=float(data.get("paid_amount", 0.0)),
        )

    @classmethod
    def new(
        cls,
        order_id: int,
        pizzas: list[Pizza],
        customer_type: CustomerType,
        payment_type: PaymentType,
        drinks: list[MenuItem] | None = None,
        table_number: int | None = None,
        delivery_address: str | None = None,
        delivery_phone: str | None = None,
    ) -> "Order":
        """Factory method for new order."""
        order = cls(
            id=order_id,
            pizzas=pizzas,
            status=OrderStatus.CREATED,
            customer_type=customer_type,
            table_number=table_number,
            delivery_address=delivery_address,
            delivery_phone=delivery_phone,
            payment_type=payment_type,
            total_price=0.0,
            creation_time=datetime.now().replace(microsecond=0).isoformat(),
            drinks=list(drinks or []),
        )
        order.recalculate_total()
        return order
