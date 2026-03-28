"""Pizzeria aggregate root."""
from __future__ import annotations

from dataclasses import dataclass, field
import random

from pizzeria.domain import CustomerType, EmployeeRole, OrderStatus, PaymentType, PizzaSize, PizzaStatus
from pizzeria.domain.exceptions import NotFoundError, PaymentError, ValidationError
from pizzeria.domain.models.counter import OrderCounter
from pizzeria.domain.models.delivery import DeliveryCoordinator
from pizzeria.domain.models.employee import Cashier, Cook, Courier, Employee, Manager
from pizzeria.domain.models.hall import Hall
from pizzeria.domain.models.kitchen import Kitchen
from pizzeria.domain.models.menu import create_default_menu
from pizzeria.domain.models.order import Order
from pizzeria.domain.models.payment import CardTerminal, CashDesk, PaymentSystem
from pizzeria.domain.models.stock import Stock
from pizzeria.domain.models.table import Table
from pizzeria.domain.models.oven import Oven

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
class Pizzeria:
    """Main system coordinator."""

    kitchen: Kitchen
    hall: Hall
    order_counter: OrderCounter
    delivery: DeliveryCoordinator
    employees: list[Employee]
    orders: list[Order] = field(default_factory=list)
    next_order_id: int = 1
    next_pizza_id: int = 1
    revenue: float = 0.0
    tips_total: float = 0.0

    def _generate_order_id(self) -> int:
        order_id = self.next_order_id
        self.next_order_id += 1
        return order_id

    def _generate_pizza_id(self) -> int:
        pizza_id = self.next_pizza_id
        self.next_pizza_id += 1
        return pizza_id

    def _find_first_by_role(self, role: EmployeeRole) -> int | None:
        for employee in self.employees:
            if employee.role == role and employee.active:
                return employee.id
        return None

    def _find_order(self, order_id: int) -> Order:
        for order in self.orders:
            if order.id == order_id:
                return order
        raise NotFoundError(f"Заказ {order_id} не найден")

    def create_dine_in_order(
        self,
        table_number: int,
        guests_count: int,
        pizza_item_ids: list[int],
        size: PizzaSize,
        payment_type: PaymentType,
        drink_item_ids: list[int] | None = None,
    ) -> Order:
        """Create new dine-in order."""
        if guests_count <= 0:
            raise ValidationError("Количество гостей должно быть больше нуля")

        drink_ids = drink_item_ids or []
        pizzas = self.order_counter.build_pizzas(
            item_ids=pizza_item_ids,
            size=size,
            pizza_id_factory=self._generate_pizza_id,
        )
        drinks = self.order_counter.build_drinks(drink_ids)

        order = Order.new(
            order_id=self._generate_order_id(),
            pizzas=pizzas,
            drinks=drinks,
            customer_type=CustomerType.DINE_IN,
            payment_type=payment_type,
            table_number=table_number,
        )
        self.hall.occupy_table(table_number=table_number, order_id=order.id)
        self.orders.append(order)
        return order

    def create_delivery_order(
        self,
        delivery_address: str,
        delivery_phone: str,
        pizza_item_ids: list[int],
        size: PizzaSize,
        payment_type: PaymentType,
        drink_item_ids: list[int] | None = None,
    ) -> Order:
        """Create new delivery order."""
        drink_ids = drink_item_ids or []
        pizzas = self.order_counter.build_pizzas(
            item_ids=pizza_item_ids,
            size=size,
            pizza_id_factory=self._generate_pizza_id,
        )
        drinks = self.order_counter.build_drinks(drink_ids)

        order = Order.new(
            order_id=self._generate_order_id(),
            pizzas=pizzas,
            drinks=drinks,
            customer_type=CustomerType.DELIVERY,
            payment_type=payment_type,
            delivery_address=delivery_address,
            delivery_phone=delivery_phone,
        )
        self.orders.append(order)
        return order

    def confirm_order(self, order_id: int) -> Order:
        """Confirm order by id."""
        order = self._find_order(order_id)
        order.confirm()
        return order

    def send_order_to_kitchen(self, order_id: int) -> Order:
        """Move order into preparing and baking pipeline."""
        order = self._find_order(order_id)

        if order.status == OrderStatus.CREATED:
            order.confirm()

        if order.status == OrderStatus.CONFIRMED:
            order.start_preparing()
            order.assigned_cook = self._find_first_by_role(EmployeeRole.COOK)

            for pizza in order.pizzas:
                self.kitchen.enqueue_pizza(pizza)
            order.start_baking()
            return order

        current_status = ORDER_STATUS_RU.get(order.status, order.status.value)
        raise ValidationError(f"Заказ {order.id} нельзя отправить на кухню из статуса '{current_status}'")

    def tick_kitchen(self, minutes: int) -> list[int]:
        """Advance kitchen simulation and update orders."""
        if minutes <= 0:
            raise ValidationError("Количество минут должно быть больше нуля")

        pizza_by_id = {pizza.id: pizza for order in self.orders for pizza in order.pizzas}
        self.kitchen.tick(minutes=minutes, pizza_by_id=pizza_by_id)

        ready_orders: list[int] = []
        for order in self.orders:
            if order.status not in (OrderStatus.BAKING, OrderStatus.PREPARING):
                continue
            if all(pizza.status == PizzaStatus.READY for pizza in order.pizzas):
                order.mark_ready()
                ready_orders.append(order.id)
        return ready_orders

    def start_delivery(self, order_id: int) -> Order:
        """Start delivery route for ready delivery order."""
        order = self._find_order(order_id)
        if order.customer_type != CustomerType.DELIVERY:
            raise ValidationError("В доставку можно отправить только заказ типа 'доставка'")
        if order.status != OrderStatus.READY:
            raise ValidationError("Перед доставкой заказ должен быть в статусе 'готов'")

        order.send_out_for_delivery()
        order.assigned_courier = self._find_first_by_role(EmployeeRole.COURIER)
        self.delivery.start(order_id=order.id)
        return order

    def tick_delivery(self, minutes: int) -> list[int]:
        """Advance delivery simulation and return arrived order ids."""
        if minutes <= 0:
            raise ValidationError("Количество минут должно быть больше нуля")
        return self.delivery.tick(minutes=minutes)

    def pay_order(self, order_id: int) -> Order:
        """Process payment for order."""
        order = self._find_order(order_id)
        if order.is_paid:
            raise PaymentError("Заказ уже оплачен")

        selected_payment = order.payment_type

        if order.customer_type == CustomerType.DELIVERY:
            if order.status != OrderStatus.OUT_FOR_DELIVERY:
                raise PaymentError("Заказ на доставку можно оплатить только после отправки курьера")
            if self.delivery.is_in_progress(order.id):
                raise PaymentError("Курьер ещё не прибыл к клиенту")

        tip_percent = 0
        tip_amount = 0.0
        if random.random() < 0.5:
            tip_percent = random.randint(10, 20)
            tip_amount = round(order.total_price * (tip_percent / 100), 2)

        paid_amount = round(order.total_price + tip_amount, 2)

        self.order_counter.payment_system.process(amount=paid_amount, payment_type=selected_payment)
        order.tip_percent = tip_percent
        order.tip_amount = tip_amount
        order.paid_amount = paid_amount
        order.is_paid = True
        self.revenue = round(self.revenue + order.total_price, 2)
        self.tips_total = round(self.tips_total + tip_amount, 2)
        return order

    def complete_order(self, order_id: int) -> Order:
        """Complete order if it is ready and paid."""
        order = self._find_order(order_id)
        if not order.is_paid:
            raise ValidationError("Перед завершением заказ должен быть оплачен")

        if order.customer_type == CustomerType.DELIVERY:
            if order.status != OrderStatus.OUT_FOR_DELIVERY:
                raise ValidationError("Заказ на доставку должен быть в статусе 'в доставке'")
            if self.delivery.is_in_progress(order.id):
                raise ValidationError("Доставка ещё не завершена")
        else:
            if order.status != OrderStatus.READY:
                raise ValidationError("Заказ в зале должен быть в статусе 'готов'")

        order.complete()
        if order.customer_type == CustomerType.DINE_IN:
            self.hall.release_table_by_order(order.id)
        return order

    def cancel_order(self, order_id: int) -> Order:
        """Cancel order and release linked resources."""
        order = self._find_order(order_id)
        order.cancel()
        if order.customer_type == CustomerType.DINE_IN:
            self.hall.release_table_by_order(order.id)
        return order

    def to_dict(self) -> dict:
        """Serialize pizzeria aggregate."""
        return {
            "kitchen": self.kitchen.to_dict(),
            "hall": self.hall.to_dict(),
            "order_counter": self.order_counter.to_dict(),
            "delivery": self.delivery.to_dict(),
            "employees": [employee.to_dict() for employee in self.employees],
            "orders": [order.to_dict() for order in self.orders],
            "next_order_id": self.next_order_id,
            "next_pizza_id": self.next_pizza_id,
            "revenue": self.revenue,
            "tips_total": self.tips_total,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Pizzeria":
        """Deserialize pizzeria aggregate."""
        kitchen = Kitchen.from_dict(data.get("kitchen", {}))
        hall = Hall.from_dict(data.get("hall", {}))
        order_counter = OrderCounter.from_dict(data.get("order_counter", {}))
        delivery = DeliveryCoordinator.from_dict(data.get("delivery", {}))
        employees = [Employee.from_dict(item) for item in data.get("employees", [])]
        orders = [Order.from_dict(item) for item in data.get("orders", [])]

        return cls(
            kitchen=kitchen,
            hall=hall,
            order_counter=order_counter,
            delivery=delivery,
            employees=employees,
            orders=orders,
            next_order_id=int(data.get("next_order_id", 1)),
            next_pizza_id=int(data.get("next_pizza_id", 1)),
            revenue=float(data.get("revenue", 0.0)),
            tips_total=float(data.get("tips_total", 0.0)),
        )


def create_default_pizzeria() -> Pizzeria:
    """Factory that creates default pizzeria configuration."""
    stock = Stock(
        ingredients={
            "тесто": 50,
            "томатный_соус": 20,
            "моцарелла": 20,
            "базилик": 10,
            "пепперони": 15,
            "грибы": 15,
            "перец": 12,
            "оливки": 12,
        },
        pizza_boxes=100,
        receipt_paper_rolls=20,
    )
    kitchen = Kitchen(
        ovens=[Oven(id=1, capacity=3), Oven(id=2, capacity=2)],
        stock=stock,
        preparation_table_capacity=4,
    )

    hall = Hall(
        tables=[
            Table(number=1, capacity=2),
            Table(number=2, capacity=4),
            Table(number=3, capacity=4),
            Table(number=4, capacity=6),
        ]
    )

    payment_system = PaymentSystem(
        card_terminal=CardTerminal(is_operational=True, is_connected=True, has_receipt_paper=True),
        cash_desk=CashDesk(cash_amount=300.0, has_receipt_paper=True),
    )

    counter = OrderCounter(menu=create_default_menu(), payment_system=payment_system)

    employees: list[Employee] = [
        Cook(employee_id=1, name="Анна Повар", salary=1200.0),
        Courier(employee_id=2, name="Иван Курьер", salary=900.0),
        Cashier(employee_id=3, name="Мария Кассир", salary=850.0),
        Manager(employee_id=4, name="Олег Менеджер", salary=1500.0),
    ]

    return Pizzeria(
        kitchen=kitchen,
        hall=hall,
        order_counter=counter,
        delivery=DeliveryCoordinator(),
        employees=employees,
    )
