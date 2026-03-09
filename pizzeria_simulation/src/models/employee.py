"""Сотрудники."""
from dataclasses import dataclass

from src.enums import EmployeeRole


@dataclass
class Employee:
    """Сотрудник."""
    id: int
    name: str
    role: EmployeeRole
    base_salary: float
    tips: float


@dataclass
class StaffTeam:
    """Команда сотрудников."""
    employees: list[Employee]
