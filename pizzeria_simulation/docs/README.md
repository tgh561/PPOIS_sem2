# Пиццерия Симулятор

Симулятор управления пиццерией с полным циклом: заказы, кухня, доставка, платежи и персонал.

## Структура проекта

```
pizzeria_simulation/
├── main.py                 # Точка входа
├── test.py                 # Быстрые тесты
├── src/
│   ├── cli/                # CLI интерфейс
│   │   └── main_cli.py
│   ├── commands/           # Команды для меню
│   │   ├── order_commands.py
│   │   ├── kitchen_commands.py
│   │   ├── payment_commands.py
│   │   ├── hall_commands.py
│   │   ├── finance_commands.py
│   │   ├── staff_commands.py
│   │   └── system_commands.py
│   ├── models/             # Модели данных
│   │   ├── order.py
│   │   ├── counter.py
│   │   ├── hall.py
│   │   ├── employee.py
│   │   ├── kitchen.py
│   │   ├── payment.py
│   │   ├── pizza.py
│   │   └── pizzeria.py
│   ├── enums/              # Перечисления
│   │   ├── order_enums.py
│   │   ├── employee_enums.py
│   │   ├── payment_enums.py
│   │   └── pizza_enums.py
│   ├── services/           # Бизнес-логика
│   │   ├── order_service.py
│   │   ├── simulation_service.py
│   │   ├── accounting_service.py
│   │   └── delivery_service.py
│   └── utils/              # Утилиты
│       ├── storage.py      # JSON сериализация
│       └── exceptions.py   # Исключения
├── tests/                  # Тесты
├── data/                   # Данные (state.json)
└── docs/                   # Документация
```

## Запуск

```bash
python main.py
```

## Тесты

```bash
pytest tests/ -v
```

## Возможности

- 📋 **Заказы**: создание заказов на месте и с доставкой
- 🪑 **Зал**: управление столиками
- 👨‍🍳 **Кухня**: симуляция приготовления заказов
- 💳 **Платежи**: наличные и карты
- 💰 **Финансы**: учёт выручки и чаевых
- 👥 **Персонал**: сотрудники с ролями

## Python 3.14

Используется современный синтаксис Python 3.14:
- `list[int]` вместо `List[int]`
- `str | None` вместо `Optional[str]`
- `StrEnum` для строковых перечислений
