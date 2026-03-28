from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class TournamentRecord:
    name: str
    event_date: date
    sport: str
    winner: str
    prize: float
    record_id: Optional[int] = None

    @property
    def earning(self) -> float:
        return round(self.prize * 0.6, 2)
