from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QWidget,
)


class PaginationBar(QWidget):
    page_changed = pyqtSignal(int)
    page_size_changed = pyqtSignal(int)

    def __init__(self) -> None:
        super().__init__()
        self._total_count = 0
        self._page_size = 10
        self._current_page = 1

        self._btn_first = QPushButton("« Первая")
        self._btn_prev = QPushButton("‹ Пред.")
        self._btn_next = QPushButton("След. ›")
        self._btn_last = QPushButton("Последняя »")

        self._label_status = QLabel()
        self._label_pages = QLabel()

        self._spin_page = QSpinBox()
        self._spin_page.setMinimum(1)
        self._spin_page.setMaximum(1)
        self._spin_page.valueChanged.connect(self._on_spin_page)

        self._combo_page_size = QComboBox()
        for n in (5, 10, 15, 25, 50):
            self._combo_page_size.addItem(str(n), n)
        self._combo_page_size.setCurrentIndex(1)
        self._combo_page_size.currentIndexChanged.connect(self._on_page_size_combo)

        self._btn_first.clicked.connect(lambda: self._go_to_page(1))
        self._btn_prev.clicked.connect(self._prev)
        self._btn_next.clicked.connect(self._next)
        self._btn_last.clicked.connect(self._last)

        row = QHBoxLayout(self)
        row.addWidget(self._btn_first)
        row.addWidget(self._btn_prev)
        row.addWidget(self._spin_page)
        row.addWidget(self._btn_next)
        row.addWidget(self._btn_last)
        row.addStretch(1)
        row.addWidget(QLabel("Записей на странице:"))
        row.addWidget(self._combo_page_size)
        row.addStretch(1)
        row.addWidget(self._label_pages)
        row.addWidget(self._label_status)

        self._update_enabled()
        self._refresh_labels()

    def set_total_count(self, total: int) -> None:
        self._total_count = max(0, total)
        pages = max(1, (self._total_count + self._page_size - 1) // self._page_size)
        if self._current_page > pages:
            self._current_page = pages
        self._spin_page.blockSignals(True)
        self._spin_page.setMaximum(pages)
        self._spin_page.setValue(self._current_page)
        self._spin_page.blockSignals(False)
        self._refresh_labels()
        self._update_enabled()

    @property
    def page_size(self) -> int:
        return self._page_size

    @property
    def current_page(self) -> int:
        return self._current_page

    def reset_to_first_page(self) -> None:
        self._go_to_page(1)

    def _total_pages(self) -> int:
        if self._total_count <= 0:
            return 1
        return max(1, (self._total_count + self._page_size - 1) // self._page_size)

    def _go_to_page(self, page: int) -> None:
        pages = self._total_pages()
        page = max(1, min(page, pages))
        if page == self._current_page and self._spin_page.value() == page:
            return
        self._current_page = page
        self._spin_page.blockSignals(True)
        self._spin_page.setValue(page)
        self._spin_page.blockSignals(False)
        self._refresh_labels()
        self._update_enabled()
        self.page_changed.emit(self._current_page)

    def _prev(self) -> None:
        self._go_to_page(self._current_page - 1)

    def _next(self) -> None:
        self._go_to_page(self._current_page + 1)

    def _last(self) -> None:
        self._go_to_page(self._total_pages())

    def _on_spin_page(self, value: int) -> None:
        self._go_to_page(int(value))

    def _on_page_size_combo(self) -> None:
        self._page_size = int(self._combo_page_size.currentData())
        pages = self._total_pages()
        if self._current_page > pages:
            self._current_page = pages
        self._spin_page.blockSignals(True)
        self._spin_page.setMaximum(pages)
        self._spin_page.setValue(self._current_page)
        self._spin_page.blockSignals(False)
        self._refresh_labels()
        self._update_enabled()
        self.page_size_changed.emit(self._page_size)
        self.page_changed.emit(self._current_page)

    def _refresh_labels(self) -> None:
        pages = self._total_pages()
        start = (self._current_page - 1) * self._page_size + 1
        end = min(self._current_page * self._page_size, self._total_count)
        if self._total_count == 0:
            start, end = 0, 0
        self._label_pages.setText(f"Страница {self._current_page} из {pages}")
        self._label_status.setText(
            f"Показано записей: {start}–{end} из {self._total_count}"
        )

    def _update_enabled(self) -> None:
        pages = self._total_pages()
        self._btn_first.setEnabled(self._current_page > 1)
        self._btn_prev.setEnabled(self._current_page > 1)
        self._btn_next.setEnabled(self._current_page < pages)
        self._btn_last.setEnabled(self._current_page < pages)
