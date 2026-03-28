#!/usr/bin/env python3
"""Генерация демонстрационных XML (≥50 осмысленных записей в каждом файле)."""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from models.tournament_record import TournamentRecord
from services.xml_storage import save_tournaments_dom

SPORTS = [
    "Теннис",
    "Футбол",
    "Хоккей",
    "Лёгкая атлетика",
    "Шахматы",
    "Дзюдо",
    "Баскетбол",
    "Парусный спорт",
    "Велоспорт",
    "Плавание",
]

FIRST = [
    "Александр",
    "Мария",
    "Иван",
    "Елена",
    "Дмитрий",
    "Анна",
    "Сергей",
    "Ольга",
    "Николай",
    "Татьяна",
]

LAST = [
    "Козлов",
    "Соколова",
    "Волков",
    "Морозова",
    "Лебедев",
    "Новикова",
    "Орлов",
    "Кузнецова",
    "Смирнов",
    "Васильева",
]


def build_set_a(n: int, start: date) -> list[TournamentRecord]:
    rows: list[TournamentRecord] = []
    for i in range(n):
        sport = SPORTS[i % len(SPORTS)]
        w = f"{FIRST[i % len(FIRST)]} {LAST[(i * 3) % len(LAST)]}"
        prize = 25_000.0 + (i * 17_500) + (i % 7) * 3_250.50
        name = f"{sport}: Кубок Северной лиги {2023 + (i // 12)} — этап {i + 1}"
        rows.append(
            TournamentRecord(
                name=name,
                event_date=start + timedelta(days=i * 11 + (i % 5)),
                sport=sport,
                winner=w,
                prize=round(prize, 2),
            )
        )
    return rows


def build_set_b(n: int, start: date) -> list[TournamentRecord]:
    rows: list[TournamentRecord] = []
    cities = ["Барселона", "Мельбурн", "Токио", "Париж", "Лондон", "Нью-Йорк"]
    for i in range(n):
        sport = SPORTS[(i * 2) % len(SPORTS)]
        w = f"{FIRST[(i * 2) % len(FIRST)]} {LAST[(i * 2) % len(LAST)]}"
        prize = 120_000.0 + (i * 41_000) + (i % 9) * 7_777.0
        city = cities[i % len(cities)]
        name = f"Международный турнир {sport} — {city} ({i + 1} сезон)"
        rows.append(
            TournamentRecord(
                name=name,
                event_date=start + timedelta(days=i * 9 + (i % 6)),
                sport=sport,
                winner=w,
                prize=round(prize, 2),
            )
        )
    return rows


def main() -> None:
    out_dir = ROOT / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    p1 = out_dir / "tournaments_demo_set1.xml"
    p2 = out_dir / "tournaments_demo_set2.xml"
    save_tournaments_dom(str(p1), build_set_a(55, date(2024, 1, 12)))
    save_tournaments_dom(str(p2), build_set_b(55, date(2023, 3, 5)))
    print(f"Written: {p1}\nWritten: {p2}")


if __name__ == "__main__":
    main()
