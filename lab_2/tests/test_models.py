from __future__ import annotations

from datetime import date

from models.tournament_model import SearchFilter, TournamentModel, record_matches
from models.tournament_record import TournamentRecord


def make_sample_record(**overrides) -> TournamentRecord:
    base = dict(
        name="Открытый чемпионат по теннису",
        event_date=date(2024, 6, 1),
        sport="Теннис",
        winner="Иван Петров",
        prize=100_000.0,
    )
    base.update(overrides)
    return TournamentRecord(**base)


def test_tournament_record_earning_property():
    rec = make_sample_record(prize=250_000.0)
    assert rec.earning == 150_000.0


def test_search_filter_normalization_strips_empty_strings():
    f = SearchFilter(
        tournament_name_substr="  ",
        event_date=date(2024, 6, 1),
        sport_exact="  Теннис ",
        winner_substr="",
    )
    nf = f.normalized()
    assert nf.tournament_name_substr is None
    assert nf.event_date == date(2024, 6, 1)
    assert nf.sport_exact == "Теннис"
    assert nf.winner_substr is None


def test_record_matches_group1_name_or_date():
    rec = make_sample_record()

    # только подстрока названия
    f1 = SearchFilter(tournament_name_substr="теннису")
    assert record_matches(rec, f1)

    # только дата
    f2 = SearchFilter(event_date=rec.event_date)
    assert record_matches(rec, f2)

    # и название, и дата не совпали → запись не подходит
    f3 = SearchFilter(tournament_name_substr="футбол", event_date=date(2000, 1, 1))
    assert not record_matches(rec, f3)


def test_record_matches_group2_sport_or_winner():
    rec = make_sample_record()

    # совпадает только вид спорта
    f1 = SearchFilter(sport_exact="Теннис")
    assert record_matches(rec, f1)

    # совпадает только ФИО по подстроке
    f2 = SearchFilter(winner_substr="петров")
    assert record_matches(rec, f2)

    # ничего не совпало
    f3 = SearchFilter(sport_exact="Футбол", winner_substr="Смирнов")
    assert not record_matches(rec, f3)


def test_record_matches_group3_range_by_prize_or_earning():
    rec = make_sample_record(prize=100_000.0)

    # диапазон только по призовым
    f1 = SearchFilter(range_min=50_000.0, range_max=120_000.0)
    assert record_matches(rec, f1)

    # диапазон только по заработку (60 000 попадает)
    f2 = SearchFilter(range_min=55_000.0, range_max=65_000.0)
    assert record_matches(rec, f2)

    # ни приз, ни заработок не попадают
    f3 = SearchFilter(range_min=200_000.0, range_max=300_000.0)
    assert not record_matches(rec, f3)


def test_record_matches_all_groups_combined_and_logic_between_groups():
    rec = make_sample_record()

    f_ok = SearchFilter(
        tournament_name_substr="чемпионат",
        sport_exact="Теннис",
        range_min=10_000.0,
        range_max=200_000.0,
    )
    assert record_matches(rec, f_ok)

    # одна из групп не выполняется → в итоге False
    f_bad = SearchFilter(
        tournament_name_substr="чемпионат",
        sport_exact="Футбол",  # группа 2 не проходит
        range_min=10_000.0,
        range_max=200_000.0,
    )
    assert not record_matches(rec, f_bad)


def test_record_matches_empty_filter_matches_everything():
    rec = make_sample_record()
    assert record_matches(rec, SearchFilter())


def test_tournament_model_add_and_delete_by_filter():
    m = TournamentModel()
    r1 = make_sample_record(name="Теннис 1", prize=50_000.0)
    r2 = make_sample_record(name="Футбол 1", sport="Футбол", prize=150_000.0)
    m.add_record(r1)
    m.add_record(r2)

    f = SearchFilter(sport_exact="Футбол")
    deleted_count, remaining = m.delete_by_filter(f)

    assert deleted_count == 1
    assert len(remaining) == 1
    assert remaining[0].sport == "Теннис"


