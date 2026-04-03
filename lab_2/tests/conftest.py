from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterator

import pytest
from PyQt6.QtWidgets import QApplication


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """Single QApplication instance for all GUI-related tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def tmp_db_path(tmp_path: Path) -> Path:
    return tmp_path / "test_tournaments.db"


