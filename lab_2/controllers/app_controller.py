from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QDialog, QFileDialog, QMessageBox

from models.tournament_model import SearchFilter, record_matches
from models.tournament_record import TournamentRecord
from services.database import TournamentDatabase
from services.xml_storage import load_tournaments_sax, save_tournaments_dom
from views.dialogs import AddRecordDialog, DeleteRecordsDialog, SearchRecordsDialog
from views.main_window import MainWindow


class AppController(QObject):
    def __init__(self, db_path: Optional[Path] = None) -> None:
        super().__init__()
        self._db_path = Path(db_path or Path(__file__).resolve().parent.parent / "data" / "tournaments.db")
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db = TournamentDatabase(self._db_path)
        self._win = MainWindow()
        self._search_dialog: Optional[SearchRecordsDialog] = None
        self._delete_dialog: Optional[DeleteRecordsDialog] = None
        self._wire()

    def _wire(self) -> None:
        w = self._win
        w.act_quit.triggered.connect(self._quit)
        w.act_add.triggered.connect(self._add_record)
        w.act_search.triggered.connect(self._open_search)
        w.act_delete.triggered.connect(self._open_delete)
        w.act_save_xml.triggered.connect(self._save_xml)
        w.act_load_xml.triggered.connect(self._load_xml)
        w.act_open_db.triggered.connect(self._open_database_file)

    def _sports(self) -> List[str]:
        return self._db.fetch_unique_sports()

    def _refresh_view(self) -> None:
        self._win.set_records(self._db.fetch_all())

    def show(self) -> None:
        self._refresh_view()
        self._win.show()

    def _quit(self) -> None:
        self._win.close()

    def _add_record(self) -> None:
        dlg = AddRecordDialog(self._win, self._sports)
        dlg.refresh_sports()
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        rec = dlg.make_record()
        self._db.insert(rec)
        self._refresh_view()

    def _open_search(self) -> None:
        if self._search_dialog is None:
            dlg = SearchRecordsDialog(self._win, self._sports)
            dlg.filter_submitted.connect(self._run_search)
            self._search_dialog = dlg
        dlg = self._search_dialog
        dlg.set_records([])
        dlg.open()

    def _run_search(self, flt: SearchFilter) -> None:
        if self._search_dialog is None:
            return
        all_rows = self._db.fetch_all()
        found = [r for r in all_rows if record_matches(r, flt)]
        self._search_dialog.set_records(found)

    def _open_delete(self) -> None:
        if self._delete_dialog is None:
            dlg = DeleteRecordsDialog(self._win, self._sports)
            dlg.delete_submitted.connect(self._perform_delete)
            self._delete_dialog = dlg
        self._delete_dialog.open()

    def _perform_delete(self, flt: SearchFilter) -> None:
        all_rows = self._db.fetch_all()
        to_remove = [r for r in all_rows if record_matches(r, flt)]
        ids = [r.record_id for r in to_remove if r.record_id is not None]
        count = self._db.delete_ids(ids)
        self._refresh_view()
        if count == 0:
            QMessageBox.information(
                self._delete_dialog or self._win,
                "Удаление",
                "Записей, удовлетворяющих условиям, не найдено. Ничего не удалено.",
            )
        else:
            QMessageBox.information(
                self._delete_dialog or self._win,
                "Удаление",
                f"Удалено записей: {count}.",
            )

    def _save_xml(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self._win,
            "Сохранить турниры в XML",
            str(Path.home() / "tournaments.xml"),
            "XML (*.xml)",
        )
        if not path:
            return
        rows = self._db.fetch_all()
        try:
            save_tournaments_dom(path, rows)
        except OSError as e:
            self._win.show_message("Ошибка", f"Не удалось сохранить файл: {e}", QMessageBox.Icon.Critical)
            return
        self._win.show_message("XML", "Данные успешно сохранены (DOM).")

    def _load_xml(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self._win,
            "Загрузить турниры из XML",
            str(Path.home()),
            "XML (*.xml)",
        )
        if not path:
            return
        try:
            rows = load_tournaments_sax(path)
        except Exception as e:  # noqa: BLE001
            self._win.show_message(
                "Ошибка",
                f"Не удалось прочитать XML (SAX): {e}",
                QMessageBox.Icon.Critical,
            )
            return
        self._db.clear_all()
        for r in rows:
            rec = TournamentRecord(
                name=r.name,
                event_date=r.event_date,
                sport=r.sport,
                winner=r.winner,
                prize=r.prize,
            )
            self._db.insert(rec)
        self._refresh_view()
        self._win.show_message("XML", f"Загружено записей: {len(rows)}.")

    def _open_database_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self._win,
            "Открыть файл SQLite",
            str(self._db_path.parent),
            "SQLite (*.db *.sqlite *.sqlite3)",
        )
        if not path:
            return
        self._db_path = Path(path)
        self._db = TournamentDatabase(self._db_path)
        self._refresh_view()
        self._win.show_message("База данных", f"Используется файл: {self._db_path}")
