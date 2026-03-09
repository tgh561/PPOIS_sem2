"""Исключения пиццерии."""


class PizzeriaError(Exception):
    """Базовое исключение для пиццерии."""
    pass


class OrderNotFoundError(PizzeriaError):
    """Заказ не найден."""
    pass


class TableNotFoundError(PizzeriaError):
    """Столик не найден."""
    pass


class PaymentError(PizzeriaError):
    """Ошибка оплаты."""
    pass


class MenuItemNotFoundError(PizzeriaError):
    """Позиция меню не найдена."""
    pass
