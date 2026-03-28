from __future__ import annotations

from datetime import date
from typing import List
from xml.dom import minidom
from xml.sax import ContentHandler, make_parser

from models.tournament_record import TournamentRecord


ROOT_TAG = "tournaments"
ITEM_TAG = "tournament"


def save_tournaments_dom(path: str, records: List[TournamentRecord]) -> None:
    doc = minidom.getDOMImplementation().createDocument(None, ROOT_TAG, None)
    root = doc.documentElement
    for rec in records:
        el = doc.createElement(ITEM_TAG)
        el.setAttribute("name", rec.name)
        el.setAttribute("event_date", rec.event_date.isoformat())
        el.setAttribute("sport", rec.sport)
        el.setAttribute("winner", rec.winner)
        el.setAttribute("prize", str(rec.prize))
        el.setAttribute("earning", str(rec.earning))
        if rec.record_id is not None:
            el.setAttribute("id", str(rec.record_id))
        root.appendChild(el)
    xml_bytes = doc.toprettyxml(encoding="utf-8", indent="  ")
    with open(path, "wb") as f:
        f.write(xml_bytes)


class _TournamentSaxHandler(ContentHandler):
    def __init__(self) -> None:
        super().__init__()
        self.records: List[TournamentRecord] = []

    def startElement(self, name, attrs) -> None: 
        if name != ITEM_TAG:
            return
        names = attrs.getNames()
        rid = int(attrs.getValue("id")) if "id" in names else None
        rec = TournamentRecord(
            record_id=rid,
            name=attrs.getValue("name"),
            event_date=date.fromisoformat(attrs.getValue("event_date")),
            sport=attrs.getValue("sport"),
            winner=attrs.getValue("winner"),
            prize=float(attrs.getValue("prize")),
        )
        self.records.append(rec)


def load_tournaments_sax(path: str) -> List[TournamentRecord]:
    parser = make_parser()
    handler = _TournamentSaxHandler()
    parser.setContentHandler(handler)
    parser.parse(path)
    return handler.records
