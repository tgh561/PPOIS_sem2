from __future__ import annotations

from datetime import date
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox

from models.tournament_record import TournamentRecord
from views.main_window import MainWindow
from views.pagination_bar import PaginationBar
from views.tournament_tree import rebuild_tournament_tree


def test_pagination_bar_basic_navigation(qapp):  # noqa: ARG001
    bar = PaginationBar()
    bar.set_total_count(95)  # при размере 10 → 10 страниц
    assert bar.current_page == 1
    assert bar.page_size == 10

    # переход вперёд / назад
    bar._next()
    assert bar.current_page == 2
    bar._on_spin_page(2)  # прямой вызов, чтобы покрыть этот путь
    bar._prev()
    assert bar.current_page == 1

    # переход на последнюю страницу
    bar._last()
    assert bar.current_page == 10

    # смена размера страницы через combo
    index_for_25 = next(
        i for i in range(bar._combo_page_size.count()) if bar._combo_page_size.itemData(i) == 25
    )
    bar._combo_page_size.setCurrentIndex(index_for_25)
    assert bar.page_size == 25
    # 95 / 25 => 4 страницы
    assert bar.current_page <= 4


def _sample_records(n: int) -> list[TournamentRecord]:
    rows: list[TournamentRecord] = []
    for i in range(n):
        rows.append(
            TournamentRecord(
                name=f"Турнир {i}",
                event_date=date(2024, 1, 1),
                sport="Теннис",
                winner=f"Игрок {i}",
                prize=1_000.0 * (i + 1),
                record_id=i + 1,
            )
        )
    return rows


def test_main_window_set_records_and_pagination(qapp):  # noqa: ARG001
    win = MainWindow()
    records = _sample_records(23)

    win.set_records(records)
    # по умолчанию страница 1, размер 10 → показывается 10 записей
    assert win._table_model.rowCount() == 10

    # переключение страницы отражается на количестве строк
    win._pagination._next()
    win._apply_slice()
    assert win._table_model.rowCount() == 10

    win._pagination._last()
    win._apply_slice()
    # последняя страница: 23 - 2*10 = 3
    assert win._table_model.rowCount() == 3

    # свойство all_records и show_message
    all_copy = win.all_records
    assert len(all_copy) == 23
    # show_message должен завершиться без ошибок
    win.show_message("Заголовок", "Текст", icon=QMessageBox.Icon.Information)


def test_rebuild_tournament_tree_populates_items(qapp, qtbot):  # type: ignore[reportUnknownParameterType]
    from PyQt6.QtWidgets import QTreeWidget

    tree = QTreeWidget()
    tree.setHeaderLabels(["Запись / поле", "Значение"])
    qtbot.addWidget(tree)

    recs = _sample_records(5)
    rebuild_tournament_tree(tree, recs)

    assert tree.topLevelItemCount() == 5
    first = tree.topLevelItem(0)
    assert first.childCount() > 0
    # первый потомок должен быть названием турнира
    child0 = first.child(0)
    assert "Название турнира" in child0.text(0)


