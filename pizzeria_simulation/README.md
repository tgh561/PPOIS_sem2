# Симулятор пиццерии CLI (перезапуск)

Проект перезапущен с нуля на основе clean architecture.

## Цели

- показать объектно-ориентированное проектирование и доменное моделирование
- держать бизнес-логику вокруг сущности `Order`
- соблюдать принципы SOLID и модульную структуру
- сохранять состояние между запусками
- обеспечивать покрытие unit-тестами

## Структура проекта

- `src/pizzeria/domain` - сущности, value objects, перечисления, исключения
- `src/pizzeria/application` - прикладные use-case сервисы
- `src/pizzeria/infrastructure` - адаптеры инфраструктуры (JSON persistence)
- `src/pizzeria/interface` - CLI-интерфейс
- `tests` - unit/integration тесты (`pytest`)

## Запуск

```bash
python main.py
```

## Запуск тестов

```bash
.venv/bin/python -m pytest -q
```

## Покрытие тестами

```bash
.venv/bin/python -m pytest \
  --cov=src/pizzeria/domain/models \
  --cov=src/pizzeria/infrastructure/persistence \
  --cov-report=term-missing
```
