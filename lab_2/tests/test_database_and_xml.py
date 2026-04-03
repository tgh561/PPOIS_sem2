from __future__ import annotations

from datetime import date
from pathlib import Path

from models.tournament_record import TournamentRecord
from services.database import TournamentDatabase
from services.xml_storage import load_tournaments_sax, save_tournaments_dom


def make_record(idx: int) -> TournamentRecord:
    return TournamentRecord(
        name=f"Турнир {idx}",
        event_date=date(2024, 1, 1).replace(day=min(28, idx or 1)),
        sport="Теннис" if idx % 2 == 0 else "Футбол",
        winner=f"Игрок {idx}",
        prize=10_000.0 * idx,
    )


def test_database_crud_and_unique_sports(tmp_db_path: Path):
    db = TournamentDatabase(tmp_db_path)

    # вставка
    rec1 = db.insert(make_record(1))
    rec2 = db.insert(make_record(2))

    assert rec1.record_id is not None
    assert rec2.record_id is not None

    # выборка всех
    all_records = db.fetch_all()
    assert len(all_records) == 2

    # обновление одной записи
    updated = TournamentRecord(
        name="Новый турнир",
        event_date=rec1.event_date,
        sport=rec1.sport,
        winner="Новый победитель",
        prize=123_456.0,
        record_id=rec1.record_id,
    )
    db.update(updated)

    again = db.fetch_all()
    up = next(r for r in again if r.record_id == rec1.record_id)
    assert up.name == "Новый турнир"
    assert up.winner == "Новый победитель"
    assert up.prize == 123_456.0
    assert up.earning == round(123_456.0 * 0.6, 2)

    # выборка видов спорта
    sports = db.fetch_unique_sports()
    assert set(sports) == {"Теннис", "Футбол"}

    # удаление по id
    deleted = db.delete_ids([rec2.record_id or -1])
    assert deleted == 1
    assert len(db.fetch_all()) == 1

    # вызываем delete_ids с пустым списком для покрытия ветки
    assert db.delete_ids([]) == 0



def test_xml_dom_and_sax_roundtrip(tmp_path: Path):
    records = [make_record(1), make_record(2)]
    xml_path = tmp_path / "roundtrip.xml"

    save_tournaments_dom(str(xml_path), records)
    assert xml_path.is_file()

    loaded = load_tournaments_sax(str(xml_path))
    assert len(loaded) == 2

    # проверяем, что основные поля совпадают
    for src, dst in zip(records, loaded, strict=True):
        assert src.name == dst.name
        assert src.event_date == dst.event_date
        assert src.sport == dst.sport
        assert src.winner == dst.winner
        assert src.prize == dst.prize


