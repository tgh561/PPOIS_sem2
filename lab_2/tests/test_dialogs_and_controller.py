from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from controllers.app_controller import AppController
from models.tournament_model import SearchFilter, record_matches
from models.tournament_record import TournamentRecord
from services.database import TournamentDatabase
from views.dialogs import AddRecordDialog, DeleteRecordsDialog, SearchRecordsDialog


def _dummy_sports() -> list[str]:
    return ["Теннис", "Футбол"]


def test_add_record_dialog_creates_record(qapp):  # noqa: ARG001
    dlg = AddRecordDialog(None, _dummy_sports)
    dlg.refresh_sports()

    dlg._name.setText("Кубок теста")
    dlg._date.setDate(dlg._date.minimumDate().addDays(1))
    dlg._sport.setCurrentIndex(0)
    dlg._winner.setText("Тест Тестов")
    dlg._prize.setValue(50_000.0)

    rec = dlg.make_record()
    assert rec.name == "Кубок теста"
    assert rec.sport in _dummy_sports()
    assert rec.winner == "Тест Тестов"
    assert rec.prize == 50_000.0
    assert rec.earning == 30_000.0


def test_filter_form_and_search_dialog_build_filter(qapp):  # noqa: ARG001
    dlg = SearchRecordsDialog(None, _dummy_sports)
    dlg._filter_form.set_sports(_dummy_sports())

    # задаём условия поиска вручную
    dlg._filter_form._name.setText("Кубок")
    dlg._filter_form._use_date.setCurrentIndex(1)  # использовать дату
    dlg._filter_form._date.setDate(dlg._filter_form._date.minimumDate().addDays(10))
    dlg._filter_form._winner.setText("Иванов")
    dlg._filter_form._rmin.setText("1000")
    dlg._filter_form._rmax.setText("200000")

    f = dlg.filter_value()
    assert isinstance(f, type(SearchFilter()))
    assert f.tournament_name_substr == "Кубок"
    assert f.range_min == 1000.0
    assert f.range_max == 200_000.0


def test_delete_dialog_emits_filter(qapp, qtbot):  # type: ignore[reportUnknownParameterType]
    dlg = DeleteRecordsDialog(None, _dummy_sports)
    qtbot.addWidget(dlg)
    dlg._filter_form.set_sports(_dummy_sports())

    emitted: list[SearchFilter] = []
    dlg.delete_submitted.connect(emitted.append)

    dlg._filter_form._name.setText("Турнир")
    dlg._submit()

    assert emitted, "Ожидали, что сигнал delete_submitted будет сгенерирован"
    assert isinstance(emitted[0], SearchFilter)


def test_app_controller_search_and_delete_logic(tmp_path: Path, qapp):  # noqa: ARG001
    db_path = tmp_path / "ctrl.db"
    db = TournamentDatabase(db_path)

    rec1 = TournamentRecord(
        name="Зимний теннисный кубок",
        event_date=date(2024, 1, 10),
        sport="Теннис",
        winner="Иван Иванов",
        prize=50_000.0,
    )
    rec2 = TournamentRecord(
        name="Летний футбольный кубок",
        event_date=date(2024, 7, 5),
        sport="Футбол",
        winner="Петр Петров",
        prize=80_000.0,
    )
    db.insert(rec1)
    db.insert(rec2)

    # используем контроллер, но подменяем его базу на нашу
    ctrl = AppController(db_path=db_path)

    # поиск по виду спорта
    flt = SearchFilter(sport_exact="Футбол")
    ctrl._run_search(flt)
    assert record_matches(rec2, flt)

    # удаление по виду спорта
    ctrl._perform_delete(flt)
    remaining = TournamentDatabase(db_path).fetch_all()
    assert len(remaining) == 1
    assert remaining[0].sport == "Теннис"

    # Восстанавливаем удалённую запись, чтобы сценарий был симметричным.
    TournamentDatabase(db_path).insert(rec2)


def test_app_controller_save_load_and_change_db(tmp_path: Path, qapp, monkeypatch):  # noqa: ARG001
    """Проверяем вспомогательные методы контроллера: show, _sports, _save_xml, _load_xml, _open_database_file."""
    db_path = tmp_path / "ctrl2.db"
    db = TournamentDatabase(db_path)
    rec = TournamentRecord(
        name="Контроллер тест",
        event_date=date(2024, 2, 2),
        sport="Теннис",
        winner="Контролёр Контролеров",
        prize=70_000.0,
    )
    db.insert(rec)

    ctrl = AppController(db_path=db_path)
    ctrl.show()  # должен вызвать _refresh_view и показать окно

    # _sports возвращает виды спорта из текущей БД
    sports = ctrl._sports()
    assert "Теннис" in sports

    # подготавливаем временный XML‑файл и патчим диалоги
    xml_path = tmp_path / "ctrl_export.xml"

    def fake_get_save_file_name(*_args, **_kwargs):
        return str(xml_path), "XML (*.xml)"

    def fake_get_open_file_name(*_args, **_kwargs):
        return str(xml_path), "XML (*.xml)"

    monkeypatch.setattr("controllers.app_controller.QFileDialog.getSaveFileName", fake_get_save_file_name)
    monkeypatch.setattr("controllers.app_controller.QFileDialog.getOpenFileName", fake_get_open_file_name)

    # сохраняем в XML и затем загружаем обратно (через контроллер)
    ctrl._save_xml()
    assert xml_path.is_file()

    # сначала очистим БД, затем убедимся, что _load_xml заполняет её снова
    TournamentDatabase(db_path).clear_all()
    assert not TournamentDatabase(db_path).fetch_all()

    ctrl._load_xml()
    reloaded = TournamentDatabase(db_path).fetch_all()
    assert reloaded, "После _load_xml база должна быть не пустой"

    # проверяем смену файла базы данных
    other_db_path = tmp_path / "other.db"

    def fake_get_open_db(*_args, **_kwargs):
        return str(other_db_path), "SQLite (*.db)"

    monkeypatch.setattr("controllers.app_controller.QFileDialog.getOpenFileName", fake_get_open_db)
    ctrl._open_database_file()
    # новый файл должен существовать (создан при инициализации TournamentDatabase)
    assert other_db_path.exists()



