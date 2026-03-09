# Дизайн проекта

## Архитектура

Проект следует паттерну **Model-Service-CLI**:

### Models (Модели)
- Чистые данные (dataclasses)
- Без бизнес-логики
- Сериализация в JSON

### Services (Сервисы)
- Бизнес-логика
- Операции над моделями
- Исключения при ошибках

### CLI (Команды)
- Пользовательский интерфейс
- Ввод/вывод
- Делегирование сервисам

## Модульная структура

### enums/
Все перечисления вынесены в отдельный модуль:
- `OrderType`, `OrderStatus` — заказы
- `EmployeeRole` — сотрудники
- `PaymentMethod` — платежи
- `PizzaBase`, `ToppingCategory` — пицца

### commands/
Команды для каждого меню:
- `order_commands` — управление заказами
- `kitchen_commands` — кухня
- `payment_commands` — платежи
- `hall_commands` — зал
- `finance_commands` — финансы
- `staff_commands` — персонал
- `system_commands` — статус системы

### services/
Бизнес-логика:
- `OrderService` — CRUD заказов
- `SimulationService` — симуляция времени
- `AccountingService` — финансы и платежи
- `DeliveryService` — доставка

## Сериализация

JSON сериализация реализована в `utils/storage.py`:
- `state_to_dict()` — конвертация в словарь
- `dict_to_state()` — восстановление из словаря
- Поддержка enum через `.value`

## Исключения

Иерархия исключений в `utils/exceptions.py`:
- `PizzeriaError` — базовое
- `OrderNotFoundError` — заказ не найден
- `TableNotFoundError` — столик не найден
- `PaymentError` — ошибка оплаты
- `MenuItemNotFoundError` — позиция меню не найдена
