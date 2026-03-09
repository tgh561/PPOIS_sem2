"""Сервис бухгалтерии."""
from src.models import PizzeriaState, Payment, PaymentMethod


class AccountingService:
    """Сервис для управления финансами и оплатами."""

    def __init__(self, state: PizzeriaState):
        self.state = state

    def record_payment(
        self,
        order_id: int,
        amount: float,
        method: PaymentMethod,
        success: bool = True,
    ) -> Payment:
        """Записывает платёж."""
        payment = Payment(
            id=self.state.next_id,
            order_id=order_id,
            amount=amount,
            method=method,
            paid_at="2026-03-09T21:00:00",
            success=success,
        )
        self.state.next_id += 1
        self.state.payments.append(payment)

        if success:
            self.state.finance.total_revenue += amount

            if method == PaymentMethod.CASH:
                self.state.order_desk.cash_register.cash_amount += amount

        return payment

    def get_payment_history(self, limit: int = 10) -> list[Payment]:
        """Получает историю платежей."""
        return self.state.payments[-limit:]

    def get_total_revenue(self) -> float:
        """Получает общую выручку."""
        return self.state.finance.total_revenue

    def get_cash_in_register(self) -> float:
        """Получает наличные в кассе."""
        return self.state.order_desk.cash_register.cash_amount

    def add_tips(self, employee_id: int, amount: float) -> None:
        """Добавляет чаевые сотруднику."""
        employee = next(
            (e for e in self.state.staff_team.employees if e.id == employee_id),
            None,
        )
        if employee:
            employee.tips += amount
            self.state.finance.total_tips += amount
