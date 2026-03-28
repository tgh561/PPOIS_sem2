from __future__ import annotations

from typing import List

from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem

from models.tournament_record import TournamentRecord


def rebuild_tournament_tree(tree: QTreeWidget, records: List[TournamentRecord]) -> None:
    tree.clear()
    for rec in records:
        root = QTreeWidgetItem([rec.name])
        root.setExpanded(True)
        fields = [
            ("Название турнира", rec.name),
            ("Дата проведения", rec.event_date.isoformat()),
            ("Вид спорта", rec.sport),
            ("ФИО победителя", rec.winner),
            ("Размер призовых", f"{rec.prize:.2f}"),
            ("Заработок победителя (60%)", f"{rec.earning:.2f}"),
        ]
        for label, value in fields:
            leaf = QTreeWidgetItem([label, value])
            root.addChild(leaf)
        tree.addTopLevelItem(root)
