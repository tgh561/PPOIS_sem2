from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path
from typing import List, Optional, Sequence

from models.tournament_record import TournamentRecord


def _connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


class TournamentDatabase:
    def __init__(self, db_path: Path) -> None:
        self._path = Path(db_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    @property
    def path(self) -> Path:
        return self._path

    def _init_schema(self) -> None:
        with _connect(self._path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tournaments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    event_date TEXT NOT NULL,
                    sport TEXT NOT NULL,
                    winner TEXT NOT NULL,
                    prize REAL NOT NULL,
                    earning REAL NOT NULL
                )
                """
            )
            conn.commit()

    def clear_all(self) -> None:
        with _connect(self._path) as conn:
            conn.execute("DELETE FROM tournaments")
            conn.commit()

    def insert(self, record: TournamentRecord) -> TournamentRecord:
        earning = record.earning
        with _connect(self._path) as conn:
            cur = conn.execute(
                """
                INSERT INTO tournaments (name, event_date, sport, winner, prize, earning)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    record.name,
                    record.event_date.isoformat(),
                    record.sport,
                    record.winner,
                    record.prize,
                    earning,
                ),
            )
            conn.commit()
            rid = int(cur.lastrowid)
        return TournamentRecord(
            name=record.name,
            event_date=record.event_date,
            sport=record.sport,
            winner=record.winner,
            prize=record.prize,
            record_id=rid,
        )

    def update(self, record: TournamentRecord) -> None:
        if record.record_id is None:
            raise ValueError("record_id required for update")
        earning = record.earning
        with _connect(self._path) as conn:
            conn.execute(
                """
                UPDATE tournaments
                SET name = ?, event_date = ?, sport = ?, winner = ?, prize = ?, earning = ?
                WHERE id = ?
                """,
                (
                    record.name,
                    record.event_date.isoformat(),
                    record.sport,
                    record.winner,
                    record.prize,
                    earning,
                    record.record_id,
                ),
            )
            conn.commit()

    def delete_ids(self, ids: Sequence[int]) -> int:
        if not ids:
            return 0
        placeholders = ",".join("?" * len(ids))
        with _connect(self._path) as conn:
            cur = conn.execute(
                f"DELETE FROM tournaments WHERE id IN ({placeholders})",
                tuple(ids),
            )
            conn.commit()
            return cur.rowcount

    def fetch_all(self) -> List[TournamentRecord]:
        with _connect(self._path) as conn:
            rows = conn.execute(
                "SELECT id, name, event_date, sport, winner, prize FROM tournaments ORDER BY id"
            ).fetchall()
        return [self._row_to_record(r) for r in rows]

    def fetch_unique_sports(self) -> List[str]:
        with _connect(self._path) as conn:
            rows = conn.execute(
                "SELECT DISTINCT sport FROM tournaments ORDER BY sport COLLATE NOCASE"
            ).fetchall()
        return [str(r[0]) for r in rows if r[0]]

    @staticmethod
    def _row_to_record(row: sqlite3.Row) -> TournamentRecord:
        return TournamentRecord(
            record_id=int(row["id"]),
            name=str(row["name"]),
            event_date=date.fromisoformat(str(row["event_date"])),
            sport=str(row["sport"]),
            winner=str(row["winner"]),
            prize=float(row["prize"]),
        )
