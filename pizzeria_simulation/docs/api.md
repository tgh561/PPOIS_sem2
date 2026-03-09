# API Документация

## Модели

### Order
```python
Order(
    id: int,
    type: OrderType,           # ON_SITE | DELIVERY
    customer_phone: str | None,
    table_id: int | None,
    delivery_address: str | None,
    items: list[OrderItem],
    status: OrderStatus,
    created_at: str,
    estimated_ready_time: str | None,
    total_price: float,
    tips_amount: float
)
```

### OrderItem
```python
OrderItem(
    id: int,
    menu_item_id: int,
    quantity: int,
    unit_price: float,
    total_price: float
)
```

### Payment
```python
Payment(
    id: int,
    order_id: int,
    amount: float,
    method: PaymentMethod,     # CASH | CARD
    paid_at: str,
    success: bool
)
```

### Employee
```python
Employee(
    id: int,
    name: str,
    role: EmployeeRole,        # COOK | WAITER | COURIER | CASHIER | ACCOUNTANT
    base_salary: float,
    tips: float
)
```

### Table
```python
Table(
    id: int,
    capacity: int,
    is_occupied: bool
)
```

### Kitchen
```python
Kitchen(
    orders_in_queue: list[int],
    orders_cooking: list[int],
    orders_baked: list[int]
)
```

## Сервисы

### OrderService
```python
OrderService(state: PizzeriaState)

# Методы
create_order(
    order_type: OrderType,
    items: list[OrderItem],
    table_id: int | None = None,
    delivery_address: str | None = None,
    customer_phone: str | None = None
) -> Order

get_order(order_id: int) -> Order
change_status(order_id: int, new_status: OrderStatus) -> None
get_active_orders() -> list[Order]
cancel_order(order_id: int) -> None
```

### SimulationService
```python
SimulationService(state: PizzeriaState)

# Методы
tick(minutes: int = 10) -> dict
get_kitchen_status() -> dict
add_to_queue(order_id: int) -> bool
```

### AccountingService
```python
AccountingService(state: PizzeriaState)

# Методы
record_payment(
    order_id: int,
    amount: float,
    method: PaymentMethod,
    success: bool = True
) -> Payment

get_payment_history(limit: int = 10) -> list[Payment]
get_total_revenue() -> float
get_cash_in_register() -> float
add_tips(employee_id: int, amount: float) -> None
```

### DeliveryService
```python
DeliveryService(state: PizzeriaState)

# Методы
create_delivery_order(
    items: list[OrderItem],
    delivery_address: str,
    customer_phone: str
) -> Order

mark_ready_for_delivery(order_id: int) -> bool
mark_delivering(order_id: int) -> bool
mark_completed(order_id: int) -> bool
```

## Утилиты

### Storage
```python
# Загрузка состояния
load_state() -> PizzeriaState

# Сохранение состояния
save_state(state: PizzeriaState) -> None

# Конвертация
state_to_dict(state: PizzeriaState) -> dict
dict_to_state(data: dict) -> PizzeriaState
```

## Исключения

```python
PizzeriaError(Exception)          # Базовое исключение
OrderNotFoundError(PizzeriaError) # Заказ не найден
TableNotFoundError(PizzeriaError) # Столик не найден
PaymentError(PizzeriaError)       # Ошибка оплаты
MenuItemNotFoundError(PizzeriaError) # Позиция меню не найдена
```

## Перечисления

### OrderType
- `ON_SITE` — заказ на месте
- `DELIVERY` — заказ с доставкой

### OrderStatus
- `CREATED` — создан
- `PAID` — оплачен
- `IN_QUEUE` — в очереди на кухню
- `COOKING` — готовится
- `BAKED` — готов
- `READY_FOR_SERVE` — готов к подаче
- `READY_FOR_DELIVERY` — готов к доставке
- `DELIVERING` — доставляется
- `COMPLETED` — завершён
- `CANCELLED` — отменён

### PaymentMethod
- `CASH` — наличные
- `CARD` — карта

### EmployeeRole
- `COOK` — повар
- `WAITER` — официант
- `COURIER` — курьер
- `CASHIER` — кассир
- `ACCOUNTANT` — бухгалтер

### PizzaBase
- `CLASSIC` — классическая
- `THIN` — тонкая
- `STUFFED` — с сырной корочкой

### ToppingCategory
- `MEAT` — мясные
- `CHEESE` — сыр
- `VEGETABLE` — овощи
- `SAUCE` — соусы
