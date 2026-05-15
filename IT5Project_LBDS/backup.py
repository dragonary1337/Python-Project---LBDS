"""
Backward-compatible exports. Prefer ``services.export.ExportService`` for new code.
"""

from pathlib import Path

from services.export import ExportService, default_export_dir


class Backup:
    """Thin wrapper around ``ExportService`` for older imports."""

    def export_books(self, db):
        path = Path("books_backup.csv")
        ExportService(db).export_books_csv(path)

    def export_transactions(self, db):
        path = Path("transactions_backup.csv")
        ExportService(db).export_transactions_csv(path)


__all__ = ["Backup", "ExportService", "default_export_dir"]
