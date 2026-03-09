"""Роли сотрудников."""
from enum import StrEnum


class EmployeeRole(StrEnum):
    """Роли сотрудников."""
    COOK = "cook"
    WAITER = "waiter"
    COURIER = "courier"
    CASHIER = "cashier"
    ACCOUNTANT = "accountant"
