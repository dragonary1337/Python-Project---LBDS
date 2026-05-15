"""CSV / text export for books, transactions, and dashboard summaries."""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path


def default_export_dir() -> Path:
    root = Path(__file__).resolve().parent.parent
    out = root / "exports"
    out.mkdir(parents=True, exist_ok=True)
    return out


class ExportService:
    def __init__(self, db):
        self.db = db

    def export_books_csv(self, path: Path | str | None = None) -> Path:
        path = Path(path) if path else default_export_dir() / f"books_{datetime.now():%Y%m%d_%H%M%S}.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db.cursor.execute(
            "SELECT id, title, author, genre, capacity, available FROM books ORDER BY id"
        )
        rows = self.db.cursor.fetchall()
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["id", "title", "author", "genre", "capacity", "available"])
            w.writerows(rows)
        return path

    def export_transactions_csv(self, path: Path | str | None = None) -> Path:
        path = Path(path) if path else default_export_dir() / f"transactions_{datetime.now():%Y%m%d_%H%M%S}.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db.cursor.execute(
            "SELECT id, borrower, book_title, borrow_date, return_date FROM transactions ORDER BY id"
        )
        rows = self.db.cursor.fetchall()
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["id", "borrower", "book_title", "borrow_date", "return_date"])
            w.writerows(rows)
        return path

    def build_dashboard_text(self, lib) -> str:
        books = lib.get_books()
        transactions = lib.get_transactions()
        total_books = len(books)
        total_copies = sum(b.capacity for b in books)
        available = sum(b.available for b in books)
        borrowed_copies = total_copies - available
        active_loans = sum(1 for t in transactions if t.return_date is None)
        lines = [
            "LBMS — Dashboard export",
            f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}",
            "",
            f"Distinct titles: {total_books}",
            f"Total copies: {total_copies}",
            f"Available copies: {available}",
            f"Borrowed copies (inventory): {borrowed_copies}",
            f"Transaction rows: {len(transactions)}",
            f"Active loans (return_date IS NULL): {active_loans}",
        ]
        return "\n".join(lines) + "\n"

    def export_dashboard_txt(self, lib, path: Path | str | None = None) -> Path:
        path = Path(path) if path else default_export_dir() / f"dashboard_{datetime.now():%Y%m%d_%H%M%S}.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.build_dashboard_text(lib), encoding="utf-8")
        return path
