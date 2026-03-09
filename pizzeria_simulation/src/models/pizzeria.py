"""Состояние пиццерии."""
from dataclasses import dataclass

from src.models.counter import OrderDesk, Menu, CashRegister, CardTerminal
from src.models.hall import DiningHall, Table
from src.models.employee import StaffTeam, Employee
from src.models.kitchen import Kitchen
from src.models.pizza import PizzaBaseItem, Topping, PizzaBase, ToppingCategory
from src.models.counter import MenuItem
from src.enums import EmployeeRole
from src.menus.menu_data import create_menu_items, PIZZA_RECIPES, DRINKS, OTHER_ITEMS


@dataclass
class CompanyFinance:
    """Финансы компании."""
    total_revenue: float
    total_tips: float


@dataclass
class PizzeriaState:
    """Состояние пиццерии."""
    next_id: int
    orders: list
    payments: list
    order_desk: OrderDesk | None
    dining_hall: DiningHall | None
    staff_team: StaffTeam | None
    kitchen: Kitchen | None
    finance: CompanyFinance

    def __post_init__(self):
        """Автоматически заполняем None значениями по умолчанию."""
        if self.order_desk is None:
            self.order_desk = create_default_order_desk()
        if self.dining_hall is None:
            self.dining_hall = create_default_dining_hall()
        if self.staff_team is None:
            self.staff_team = create_default_staff_team()
        if self.kitchen is None:
            self.kitchen = create_default_kitchen()


def create_default_state() -> PizzeriaState:
    """Создаёт состояние по умолчанию - ВСЁ СВОБОДНО."""
    return PizzeriaState(
        next_id=1,
        orders=[],
        payments=[],
        order_desk=None,
        dining_hall=None,
        staff_team=None,
        kitchen=None,
        finance=CompanyFinance(0.0, 0.0)
    )


def create_default_order_desk() -> OrderDesk:
    """Стойка с расширенным меню."""
    pizza_bases = [
        PizzaBaseItem(id=1, name="Классическая", base_type=PizzaBase.CLASSIC, price=2.0),
        PizzaBaseItem(id=2, name="Тонкая", base_type=PizzaBase.THIN, price=3.0),
        PizzaBaseItem(id=3, name="С сырной корочкой", base_type=PizzaBase.STUFFED, price=4.0),
    ]

    toppings = [
        Topping(id=1, name="Пепперони", price=2.5, category=ToppingCategory.MEAT, is_available=True),
        Topping(id=2, name="Ветчина", price=2.0, category=ToppingCategory.MEAT, is_available=True),
        Topping(id=3, name="Моцарелла", price=1.5, category=ToppingCategory.CHEESE, is_available=True),
        Topping(id=4, name="Грибы", price=1.0, category=ToppingCategory.VEGETABLE, is_available=True),
        Topping(id=5, name="Маслины", price=1.0, category=ToppingCategory.VEGETABLE, is_available=True),
        Topping(id=6, name="Томатный соус", price=0.5, category=ToppingCategory.SAUCE, is_available=True),
    ]

    # Создаём меню из menu_data
    menu_items = create_menu_items()
    menu = Menu(items=menu_items)
    menu.pizza_bases = pizza_bases
    menu.toppings = toppings

    cash_register = CashRegister(id=1, cash_amount=500.0, has_receipt_paper=True)
    card_terminal = CardTerminal(id=1, is_working=True, is_online=True, has_receipt_paper=True)

    return OrderDesk(menu, cash_register, card_terminal, "+375291234567")


def create_default_dining_hall() -> DiningHall:
    """Зал с 5 столиками - ВСЕ СВОБОДНЫ."""
    tables = [
        Table(id=1, capacity=2, is_occupied=False),  # Маленький столик
        Table(id=2, capacity=4, is_occupied=False),  # Средний столик
        Table(id=3, capacity=4, is_occupied=False),  # Средний столик
        Table(id=4, capacity=6, is_occupied=False),  # Большой столик
        Table(id=5, capacity=8, is_occupied=False),  # Для компаний
    ]
    return DiningHall(tables)


def create_default_staff_team() -> StaffTeam:
    """Базовая команда."""
    employees = [
        Employee(id=1, name="Мария Сидорова", role=EmployeeRole.COOK, base_salary=1000.0, tips=0.0),
        Employee(id=2, name="Иван Петров", role=EmployeeRole.WAITER, base_salary=800.0, tips=0.0),
        Employee(id=3, name="Алексей Козлов", role=EmployeeRole.COURIER, base_salary=700.0, tips=0.0),
        Employee(id=4, name="Ольга Иванова", role=EmployeeRole.CASHIER, base_salary=600.0, tips=0.0),
    ]
    return StaffTeam(employees)


def create_default_kitchen() -> Kitchen:
    """Пустая кухня."""
    return Kitchen(orders_in_queue=[], orders_cooking=[], orders_baked=[])
