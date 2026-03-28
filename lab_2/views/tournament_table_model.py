from __future__ import annotations

from typing import List, Optional

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt6.QtGui import QColor

from models.tournament_record import TournamentRecord


class TournamentTableModel(QAbstractTableModel):
    HEADERS = [
        "ID",
        "Название турнира",
        "Дата",
        "Вид спорта",
        "ФИО победителя",
        "Призовые",
        "Заработок победителя (60%)",
    ]

    def __init__(self) -> None:
        super().__init__()
        self._rows: List[TournamentRecord] = []

    def set_records(self, rows: List[TournamentRecord]) -> None:
        self.beginResetModel()
        self._rows = list(rows)
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        return 0 if parent.isValid() else len(self._rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        return 0 if parent.isValid() else len(self.HEADERS)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):  # noqa: N802
        if not index.isValid() or index.row() >= len(self._rows):
            return None
        rec = self._rows[index.row()]
        col = index.column()
        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:
                return str(rec.record_id) if rec.record_id is not None else ""
            if col == 1:
                return rec.name
            if col == 2:
                return rec.event_date.isoformat()
            if col == 3:
                return rec.sport
            if col == 4:
                return rec.winner
            if col == 5:
                return f"{rec.prize:.2f}"
            if col == 6:
                return f"{rec.earning:.2f}"
        if role == Qt.ItemDataRole.TextAlignmentRole and col >= 5:
            return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        if role == Qt.ItemDataRole.BackgroundRole and col == 6:
            return QColor(240, 248, 255)
        return None

    def headerData(  # noqa: N802
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return self.HEADERS[section]
        return str(section + 1)

    def record_at(self, row: int) -> Optional[TournamentRecord]:
        if 0 <= row < len(self._rows):
            return self._rows[row]
        return None
