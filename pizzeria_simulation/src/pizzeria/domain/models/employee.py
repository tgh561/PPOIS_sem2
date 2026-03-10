"""Employee domain models."""
from __future__ import annotations

from dataclasses import dataclass, field

from pizzeria.domain import EmployeeRole


@dataclass(slots=True)
class Employee:
    """Base employee class."""

    id: int
    name: str
    role: EmployeeRole
    salary: float
    active: bool = True

    def to_dict(self) -> dict:
        """Serialize employee."""
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role.value,
            "salary": self.salary,
            "active": self.active,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Employee":
        """Deserialize employee by role."""
        role = EmployeeRole(data["role"])
        factory: dict[EmployeeRole, type[Employee]] = {
            EmployeeRole.COOK: Cook,
            EmployeeRole.COURIER: Courier,
            EmployeeRole.CASHIER: Cashier,
            EmployeeRole.MANAGER: Manager,
        }
        employee_class = factory.get(role, Employee)
        if employee_class is Employee:
            return cls(
                id=int(data["id"]),
                name=str(data["name"]),
                role=role,
                salary=float(data["salary"]),
                active=bool(data.get("active", True)),
            )
        return employee_class(
            employee_id=int(data["id"]),
            name=str(data["name"]),
            salary=float(data["salary"]),
            active=bool(data.get("active", True)),
        )


@dataclass(slots=True)
class Cook(Employee):
    """Cook role."""

    role: EmployeeRole = field(default=EmployeeRole.COOK, init=False)

    def __init__(self, employee_id: int, name: str, salary: float, active: bool = True) -> None:
        super().__init__(id=employee_id, name=name, role=EmployeeRole.COOK, salary=salary, active=active)


@dataclass(slots=True)
class Courier(Employee):
    """Courier role."""

    role: EmployeeRole = field(default=EmployeeRole.COURIER, init=False)

    def __init__(self, employee_id: int, name: str, salary: float, active: bool = True) -> None:
        super().__init__(id=employee_id, name=name, role=EmployeeRole.COURIER, salary=salary, active=active)


@dataclass(slots=True)
class Cashier(Employee):
    """Cashier role."""

    role: EmployeeRole = field(default=EmployeeRole.CASHIER, init=False)

    def __init__(self, employee_id: int, name: str, salary: float, active: bool = True) -> None:
        super().__init__(id=employee_id, name=name, role=EmployeeRole.CASHIER, salary=salary, active=active)


@dataclass(slots=True)
class Manager(Employee):
    """Manager role."""

    role: EmployeeRole = field(default=EmployeeRole.MANAGER, init=False)

    def __init__(self, employee_id: int, name: str, salary: float, active: bool = True) -> None:
        super().__init__(id=employee_id, name=name, role=EmployeeRole.MANAGER, salary=salary, active=active)
