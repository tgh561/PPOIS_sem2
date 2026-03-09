"""Tests for CLI commands."""
import pytest
from src.models import create_default_state, OrderType, OrderStatus
from src.commands import (
    handle_hall_menu,
    handle_finance_menu,
    handle_staff_menu,
    print_system_status,
)


class TestHallCommands:
    def test_handle_hall_menu(self, capsys: pytest.CaptureFixture) -> None:
        state = create_default_state()
        handle_hall_menu(state)

        captured = capsys.readouterr()
        assert "ЗАЛ" in captured.out
        assert "Столик" in captured.out
        assert "свободен" in captured.out


class TestFinanceCommands:
    def test_handle_finance_menu(self, capsys: pytest.CaptureFixture) -> None:
        state = create_default_state()
        handle_finance_menu(state)

        captured = capsys.readouterr()
        assert "ФИНАНСЫ" in captured.out
        assert "Выручка" in captured.out


class TestStaffCommands:
    def test_handle_staff_menu(self, capsys: pytest.CaptureFixture) -> None:
        state = create_default_state()
        handle_staff_menu(state)

        captured = capsys.readouterr()
        assert "ПЕРСОНАЛ" in captured.out
        assert len(state.staff_team.employees) > 0


class TestSystemCommands:
    def test_print_system_status(self, capsys: pytest.CaptureFixture) -> None:
        state = create_default_state()
        print_system_status(state)

        captured = capsys.readouterr()
        assert "СТАТУС СИСТЕМЫ" in captured.out
        assert "Заказов" in captured.out
        assert "Столиков" in captured.out
