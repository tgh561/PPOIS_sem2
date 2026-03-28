"""Application bootstrap."""
from __future__ import annotations

from pathlib import Path

from pizzeria.application.services import PizzeriaService
from pizzeria.infrastructure.persistence import JsonStateRepository
from pizzeria.interface.cli import CliApp


def run_cli(state_file: Path) -> None:
    """Run CLI with persisted state."""
    repository = JsonStateRepository(state_file)
    pizzeria = repository.load()
    service = PizzeriaService(pizzeria)
    app = CliApp(service)
    app.run()
    repository.save(service.pizzeria)
