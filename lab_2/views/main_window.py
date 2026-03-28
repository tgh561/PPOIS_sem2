from __future__ import annotations

from typing import List, Optional

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QHeaderView,
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QTabWidget,
    QTableView,
    QToolBar,
    QTreeWidget,
    QVBoxLayout,
    QWidget,
)

from models.tournament_record import TournamentRecord
from views.pagination_bar import PaginationBar
from views.tournament_table_model import TournamentTableModel
from views.tournament_tree import rebuild_tournament_tree


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Турниры — управление данными (MVC, PyQt6)")
        self.resize(1100, 640)

        self._all_records: List[TournamentRecord] = []
        self._table_model = TournamentTableModel()
        self._table = QTableView()
        self._table.setModel(self._table_model)
        self._table.setAlternatingRowColors(True)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setStretchLastSection(True)

        self._pagination = PaginationBar()
        self._pagination.page_changed.connect(self._apply_slice)
        self._pagination.page_size_changed.connect(self._apply_slice)

        table_tab = QWidget()
        tlay = QVBoxLayout(table_tab)
        tlay.addWidget(self._table)
        tlay.addWidget(self._pagination)

        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(["Запись / поле", "Значение"])
        self._tree.header().setStretchLastSection(True)

        tabs = QTabWidget()
        tabs.addTab(table_tab, "Таблица")
        tabs.addTab(self._tree, "Дерево (поля)")

        self.setCentralWidget(tabs)
        self._status = QStatusBar()
        self.setStatusBar(self._status)

        self._build_actions()
        self._build_menu_toolbar()
        self.set_records([])

    def _build_actions(self) -> None:
        self.act_quit = QAction("Выход", self)
        self.act_quit.setShortcut("Ctrl+Q")

        self.act_add = QAction("Добавить запись…", self)
        self.act_add.setShortcut("Ctrl+N")

        self.act_search = QAction("Поиск…", self)
        self.act_search.setShortcut("Ctrl+F")

        self.act_delete = QAction("Удаление по условию…", self)
        self.act_delete.setShortcut("Ctrl+D")

        self.act_save_xml = QAction("Сохранить в XML…", self)
        self.act_save_xml.setShortcut("Ctrl+S")

        self.act_load_xml = QAction("Загрузить из XML…", self)
        self.act_load_xml.setShortcut("Ctrl+O")

        self.act_open_db = QAction("Открыть базу SQLite…", self)

    def _build_menu_toolbar(self) -> None:
        mb = self.menuBar()
        file_m = mb.addMenu("Файл")
        file_m.addAction(self.act_open_db)
        file_m.addSeparator()
        file_m.addAction(self.act_save_xml)
        file_m.addAction(self.act_load_xml)
        file_m.addSeparator()
        file_m.addAction(self.act_quit)

        data_m = mb.addMenu("Данные")
        data_m.addAction(self.act_add)
        data_m.addAction(self.act_search)
        data_m.addAction(self.act_delete)

        tb = QToolBar("Главная")
        tb.setMovable(False)
        self.addToolBar(tb)
        for a in (
            self.act_add,
            self.act_search,
            self.act_delete,
            self.act_save_xml,
            self.act_load_xml,
            self.act_open_db,
        ):
            tb.addAction(a)

    def set_records(self, records: List[TournamentRecord]) -> None:
        self._all_records = list(records)
        rebuild_tournament_tree(self._tree, self._all_records)
        self._pagination.set_total_count(len(self._all_records))
        self._apply_slice()
        self._status.showMessage(f"Всего записей в базе: {len(self._all_records)}")

    def _apply_slice(self, *_args) -> None:
        ps = self._pagination.page_size
        page = self._pagination.current_page
        start = (page - 1) * ps
        chunk = self._all_records[start : start + ps]
        self._table_model.set_records(chunk)

    @property
    def all_records(self) -> List[TournamentRecord]:
        return list(self._all_records)

    def show_message(self, title: str, text: str, icon: QMessageBox.Icon = QMessageBox.Icon.Information) -> None:
        box = QMessageBox(self)
        box.setIcon(icon)
        box.setWindowTitle(title)
        box.setText(text)
        box.exec()
