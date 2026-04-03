from __future__ import annotations

from datetime import date

from PyQt6.QtCore import QModelIndex, Qt

from models.tournament_record import TournamentRecord
from services.xml_storage import save_tournaments_dom
from views.tournament_table_model import TournamentTableModel


def _record_with_id() -> TournamentRecord:
    return TournamentRecord(
        name="Турнир с id",
        event_date=date(2024, 3, 3),
        sport="Теннис",
        winner="ID Тестов",
        prize=33_333.0,
        record_id=7,
    )


def test_tournament_table_model_roles_and_invalid_indexes(qapp):  # noqa: ARG001
    model = TournamentTableModel()
    rec = _record_with_id()
    model.set_records([rec])

    # корректный индекс
    idx_id = model.index(0, 0)  # type: ignore[arg-type]
    assert model.data(idx_id, Qt.ItemDataRole.DisplayRole) == str(rec.record_id)

    # выравнивание и фон для денежного столбца
    idx_prize = model.index(0, 5)  # type: ignore[arg-type]
    align = model.data(idx_prize, Qt.ItemDataRole.TextAlignmentRole)
    assert align & Qt.AlignmentFlag.AlignRight

    idx_earning = model.index(0, 6)  # type: ignore[arg-type]
    bg = model.data(idx_earning, Qt.ItemDataRole.BackgroundRole)
    assert bg is not None

    # заголовки
    assert model.headerData(0, Qt.Orientation.Horizontal) == "ID"
    assert model.headerData(0, Qt.Orientation.Vertical) == "1"

    # невалидный индекс
    invalid = QModelIndex()
    assert model.data(invalid, Qt.ItemDataRole.DisplayRole) is None
    assert model.record_at(-1) is None
    assert model.record_at(5) is None


def test_save_tournaments_dom_sets_id_attribute(tmp_path):
    rec = _record_with_id()
    xml_path = tmp_path / "with_id.xml"
    save_tournaments_dom(str(xml_path), [rec])

    text = xml_path.read_text(encoding="utf-8")
    # удостоверимся, что атрибут id присутствует
    assert 'id="7"' in text


