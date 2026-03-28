from __future__ import annotations

from typing import Callable, List, Optional

from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from models.tournament_model import SearchFilter
from models.tournament_record import TournamentRecord
from views.pagination_bar import PaginationBar
from views.tournament_table_model import TournamentTableModel


class AddRecordDialog(QDialog):
    def __init__(self, parent: Optional[QWidget], sports_provider: Callable[[], List[str]]) -> None:
        super().__init__(parent)
        self.setWindowTitle("Добавить запись о турнире")
        self._sports_provider = sports_provider

        self._name = QLineEdit()
        self._date = QDateEdit()
        self._date.setCalendarPopup(True)
        self._date.setDisplayFormat("yyyy-MM-dd")
        self._date.setDate(QDate.currentDate())

        self._sport = QComboBox()
        self._sport.setEditable(True)
        self._sport.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        self._winner = QLineEdit()

        self._prize = QDoubleSpinBox()
        self._prize.setRange(0.0, 1e12)
        self._prize.setDecimals(2)
        self._prize.setSingleStep(1000.0)
        self._prize.setValue(100_000.0)

        self._earning_label = QLabel()
        self._earning_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._prize.valueChanged.connect(self._update_earning_preview)
        self._update_earning_preview()

        form = QFormLayout()
        form.addRow("Название турнира:", self._name)
        form.addRow("Дата проведения:", self._date)
        form.addRow("Вид спорта:", self._sport)
        form.addRow("ФИО победителя:", self._winner)
        form.addRow("Размер призовых:", self._prize)
        form.addRow("Заработок победителя (60%):", self._earning_label)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._try_accept)
        buttons.rejected.connect(self.reject)

        root = QVBoxLayout(self)
        root.addLayout(form)
        root.addWidget(buttons)

        self.refresh_sports()

    def refresh_sports(self) -> None:
        current = self._sport.currentText().strip()
        self._sport.blockSignals(True)
        self._sport.clear()
        for s in self._sports_provider():
            self._sport.addItem(s)
        if current:
            idx = self._sport.findText(current)
            if idx >= 0:
                self._sport.setCurrentIndex(idx)
            else:
                self._sport.setEditText(current)
        self._sport.blockSignals(False)

    def _update_earning_preview(self) -> None:
        v = float(self._prize.value())
        self._earning_label.setText(f"{v * 0.6:,.2f}".replace(",", " "))

    def _try_accept(self) -> None:
        if not self._name.text().strip():
            QMessageBox.warning(self, "Ошибка", "Укажите название турнира.")
            return
        sport = self._sport.currentText().strip()
        if not sport:
            QMessageBox.warning(self, "Ошибка", "Укажите вид спорта.")
            return
        if not self._winner.text().strip():
            QMessageBox.warning(self, "Ошибка", "Укажите ФИО победителя.")
            return
        self.accept()

    def make_record(self) -> TournamentRecord:
        d = self._date.date().toPyDate()
        return TournamentRecord(
            name=self._name.text().strip(),
            event_date=d,
            sport=self._sport.currentText().strip(),
            winner=self._winner.text().strip(),
            prize=float(self._prize.value()),
        )


class _FilterForm(QWidget):
    def __init__(self) -> None:
        super().__init__()
        g1 = QGroupBox("Условие 1: название турнира или дата")
        self._name = QLineEdit()
        self._name.setPlaceholderText("Часть названия…")
        self._date = QDateEdit()
        self._date.setCalendarPopup(True)
        self._date.setDisplayFormat("yyyy-MM-dd")
        self._date.setDate(QDate.currentDate())
        self._date.setMinimumDate(QDate.fromString("1900-01-01", Qt.DateFormat.ISODate))
        self._use_date = QComboBox()
        self._use_date.addItem("Игнорировать дату", False)
        self._use_date.addItem("Указать дату", True)
        self._use_date.currentIndexChanged.connect(self._toggle_date)
        row1 = QFormLayout(g1)
        row1.addRow("Название (частично):", self._name)
        row1.addRow("", self._use_date)
        row1.addRow("Дата:", self._date)
        self._toggle_date()

        g2 = QGroupBox("Условие 2: вид спорта или ФИО победителя")
        self._sport = QComboBox()
        self._winner = QLineEdit()
        self._winner.setPlaceholderText("Часть ФИО…")
        row2 = QFormLayout(g2)
        row2.addRow("Вид спорта:", self._sport)
        row2.addRow("ФИО (частично):", self._winner)

        g3 = QGroupBox("Условие 3: диапазон по призовым или заработку победителя")
        self._rmin = QLineEdit()
        self._rmin.setPlaceholderText("не задано")
        self._rmax = QLineEdit()
        self._rmax.setPlaceholderText("не задано")
        row3 = QFormLayout(g3)
        row3.addRow("Минимум (приз / заработок):", self._rmin)
        row3.addRow("Максимум (приз / заработок):", self._rmax)

        lay = QVBoxLayout(self)
        lay.addWidget(g1)
        lay.addWidget(g2)
        lay.addWidget(g3)

    @staticmethod
    def _parse_optional_float(raw: str):
        t = raw.strip().replace(" ", "").replace(",", ".")
        if not t:
            return None
        try:
            return float(t)
        except ValueError as exc:
            raise ValueError from exc

    def _toggle_date(self) -> None:
        use = bool(self._use_date.currentData())
        self._date.setEnabled(use)

    def set_sports(self, sports: List[str]) -> None:
        self._sport.blockSignals(True)
        self._sport.clear()
        self._sport.addItem("— любой —", None)
        for s in sports:
            self._sport.addItem(s, s)
        self._sport.setCurrentIndex(0)
        self._sport.blockSignals(False)

    def build_filter(self) -> SearchFilter:
        name = self._name.text().strip() or None
        use_date = bool(self._use_date.currentData())
        ev_date = self._date.date().toPyDate() if use_date else None

        sport = self._sport.currentData()
        sport_val = sport.strip() if isinstance(sport, str) and sport.strip() else None
        winner = self._winner.text().strip() or None

        try:
            rmin = _FilterForm._parse_optional_float(self._rmin.text())
            rmax = _FilterForm._parse_optional_float(self._rmax.text())
        except ValueError:
            raise

        return SearchFilter(
            tournament_name_substr=name,
            event_date=ev_date,
            sport_exact=sport_val,
            winner_substr=winner,
            range_min=rmin,
            range_max=rmax,
        )


class SearchRecordsDialog(QDialog):
    """Диалог поиска: условия и таблица результатов с пагинацией."""

    filter_submitted = pyqtSignal(object)

    def __init__(self, parent: Optional[QWidget], sports_provider: Callable[[], List[str]]) -> None:
        super().__init__(parent)
        self.setWindowTitle("Поиск записей")
        self.setMinimumSize(900, 560)
        self._sports_provider = sports_provider
        self._filter_form = _FilterForm()
        self._model = TournamentTableModel()
        self._view = QTableView()
        self._view.setModel(self._model)
        self._view.horizontalHeader().setStretchLastSection(True)
        self._view.setAlternatingRowColors(True)
        self._all_results: List[TournamentRecord] = []

        self._pagination = PaginationBar()
        self._pagination.page_changed.connect(self._show_page)
        self._pagination.page_size_changed.connect(self._show_page)

        btn_search = QPushButton("Найти")

        top = QHBoxLayout()
        top.addWidget(self._filter_form, stretch=2)
        col = QVBoxLayout()
        col.addStretch(1)
        col.addWidget(btn_search)
        col.addStretch(1)
        top.addLayout(col)

        root = QVBoxLayout(self)
        root.addLayout(top)
        root.addWidget(QLabel("Результаты:"))
        root.addWidget(self._view)
        root.addWidget(self._pagination)

        btn_close = QPushButton("Закрыть")
        btn_close.clicked.connect(self.accept)
        root.addWidget(btn_close)

        btn_search.clicked.connect(self._submit_filter)

    def showEvent(self, event) -> None:  # noqa: N802
        self._filter_form.set_sports(self._sports_provider())
        super().showEvent(event)

    def set_records(self, records: List[TournamentRecord]) -> None:
        self._all_results = list(records)
        self._pagination.reset_to_first_page()
        self._pagination.set_total_count(len(self._all_results))
        self._show_page()

    def _submit_filter(self) -> None:
        try:
            f = self._filter_form.build_filter()
        except ValueError:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Некорректное число в полях диапазона. Используйте точку как разделитель.",
            )
            return
        if f.range_min is not None and f.range_max is not None and f.range_min > f.range_max:
            QMessageBox.warning(self, "Ошибка", "Минимум диапазона не может быть больше максимума.")
            return
        self.filter_submitted.emit(f)

    def filter_value(self) -> SearchFilter:
        return self._filter_form.build_filter()

    def _show_page(self, *_args) -> None:
        ps = self._pagination.page_size
        page = self._pagination.current_page
        start = (page - 1) * ps
        chunk = self._all_results[start : start + ps]
        self._model.set_records(chunk)


class DeleteRecordsDialog(QDialog):
    """Отдельный диалог удаления по тем же условиям, что и поиск (вариант 11)."""

    delete_submitted = pyqtSignal(object)

    def __init__(self, parent: Optional[QWidget], sports_provider: Callable[[], List[str]]) -> None:
        super().__init__(parent)
        self.setWindowTitle("Удаление записей по условию")
        self.setMinimumWidth(520)
        self._sports_provider = sports_provider
        self._filter_form = _FilterForm()

        btn_delete = QPushButton("Удалить записи по условию")
        btn_delete.clicked.connect(self._submit)
        btn_close = QPushButton("Закрыть")
        btn_close.clicked.connect(self.reject)

        row = QHBoxLayout()
        row.addWidget(btn_delete)
        row.addStretch(1)
        row.addWidget(btn_close)

        root = QVBoxLayout(self)
        root.addWidget(self._filter_form)
        root.addLayout(row)

    def showEvent(self, event) -> None:  # noqa: N802
        self._filter_form.set_sports(self._sports_provider())
        super().showEvent(event)

    def _submit(self) -> None:
        try:
            f = self._filter_form.build_filter()
        except ValueError:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Некорректное число в полях диапазона.",
            )
            return
        if f.range_min is not None and f.range_max is not None and f.range_min > f.range_max:
            QMessageBox.warning(self, "Ошибка", "Минимум диапазона не может быть больше максимума.")
            return
        self.delete_submitted.emit(f)