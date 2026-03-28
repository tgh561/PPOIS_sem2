from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Optional, Sequence, Tuple

from .tournament_record import TournamentRecord


@dataclass
class SearchFilter:

    tournament_name_substr: Optional[str] = None
    event_date: Optional[date] = None
    sport_exact: Optional[str] = None
    winner_substr: Optional[str] = None
    range_min: Optional[float] = None
    range_max: Optional[float] = None

    def _norm_str(self, s: Optional[str]) -> Optional[str]:
        if s is None:
            return None
        t = s.strip()
        return t if t else None

    def normalized(self) -> "SearchFilter":
        return SearchFilter(
            tournament_name_substr=self._norm_str(self.tournament_name_substr),
            event_date=self.event_date,
            sport_exact=self._norm_str(self.sport_exact),
            winner_substr=self._norm_str(self.winner_substr),
            range_min=self.range_min,
            range_max=self.range_max,
        )


def record_matches(record: TournamentRecord, f: SearchFilter) -> bool:
    f = f.normalized()

    g1_active = f.tournament_name_substr is not None or f.event_date is not None
    if g1_active:
        name_ok = False
        if f.tournament_name_substr:
            name_ok = f.tournament_name_substr.lower() in record.name.lower()
        date_ok = f.event_date is not None and record.event_date == f.event_date
        if not (name_ok or date_ok):
            return False

    g2_active = f.sport_exact is not None or f.winner_substr is not None
    if g2_active:
        sport_ok = f.sport_exact is not None and record.sport == f.sport_exact
        winner_ok = False
        if f.winner_substr:
            winner_ok = f.winner_substr.lower() in record.winner.lower()
        if not (sport_ok or winner_ok):
            return False

    g3_active = f.range_min is not None or f.range_max is not None
    if g3_active:
        lo = f.range_min if f.range_min is not None else float("-inf")
        hi = f.range_max if f.range_max is not None else float("inf")
        p, e = record.prize, record.earning
        in_range = (lo <= p <= hi) or (lo <= e <= hi)
        if not in_range:
            return False

    return True


class TournamentModel:
    def __init__(self) -> None:
        self._records: List[TournamentRecord] = []

    @property
    def records(self) -> Sequence[TournamentRecord]:
        return self._records

    def set_records(self, records: List[TournamentRecord]) -> None:
        self._records = list(records)

    def add_record(self, record: TournamentRecord) -> None:
        self._records.append(record)

    def apply_filter(self, f: SearchFilter) -> List[TournamentRecord]:
        return [r for r in self._records if record_matches(r, f)]

    def delete_by_filter(self, f: SearchFilter) -> Tuple[int, List[TournamentRecord]]:
        to_keep = [r for r in self._records if not record_matches(r, f)]
        deleted = len(self._records) - len(to_keep)
        self._records = to_keep
        return deleted, to_keep
