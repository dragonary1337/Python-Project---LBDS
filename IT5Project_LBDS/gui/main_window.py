# -*- coding: utf-8 -*-
"""
Main window — layout similar to the original GUI.py:
  top bar (title, user, actions, logout)
  row of four statistics
  left: books table, right: transactions table

User list and export use modal dialogs instead of extra pages so the UI stays familiar
and most of the view logic lives in this single file.
"""

import os
import subprocess
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from auth import Auth
from library import Library
from models import Book, User
from services.export import ExportService, default_export_dir

from .dialogs import BookDialog, BorrowDialog
from .styles import GLOBAL_STYLE, PALETTE
from .widgets import StatCard


# ---------------------------------------------------------------------------
# User list dialog (table + delete; logic in auth.py)
# ---------------------------------------------------------------------------
class UserListDialog(QDialog):
    def __init__(self, parent, auth: Auth, my_user_id: int):
        super().__init__(parent)
        self.auth = auth
        self.my_user_id = my_user_id
        self.setWindowTitle("User management")
        self.setMinimumSize(420, 360)
        self.setStyleSheet(GLOBAL_STYLE)

        layout = QVBoxLayout(self)
        tip = QLabel("You cannot delete the account you are currently logged in with.")
        tip.setStyleSheet(f"color: {PALETTE['muted']};")
        layout.addWidget(tip)

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["ID", "Username"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        row = QHBoxLayout()
        del_btn = QPushButton("Delete selected user")
        del_btn.setObjectName("danger")
        del_btn.clicked.connect(self._delete_selected)
        row.addWidget(del_btn)
        row.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        row.addWidget(close_btn)
        layout.addLayout(row)

        self._reload_table()

    def _reload_table(self):
        rows = self.auth.list_users_public()
        self.table.setRowCount(len(rows))
        for i, (uid, name) in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(uid)))
            item_name = QTableWidgetItem(name)
            if uid == self.my_user_id:
                item_name.setForeground(QColor(PALETTE["accent"]))
            self.table.setItem(i, 1, item_name)

    def _delete_selected(self):
        r = self.table.currentRow()
        if r < 0:
            QMessageBox.warning(self, "Notice", "Please select a user row first.")
            return
        uid = int(self.table.item(r, 0).text())
        name = self.table.item(r, 1).text()
        ok = QMessageBox.question(
            self, "Confirm", f"Delete user \"{name}\"?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if ok != QMessageBox.Yes:
            return
        success, msg = self.auth.delete_user(uid, self.my_user_id)
        if not success:
            QMessageBox.warning(self, "Cannot delete", msg)
        else:
            QMessageBox.information(self, "Done", msg)
        self._reload_table()


# ---------------------------------------------------------------------------
# Export / preview dialog (uses services/export.py)
# ---------------------------------------------------------------------------
class ExportDataDialog(QDialog):
    def __init__(self, parent, export_service: ExportService, lib: Library):
        super().__init__(parent)
        self.export_service = export_service
        self.lib = lib
        self.setWindowTitle("Export / preview data")
        self.setMinimumSize(520, 420)
        self.setStyleSheet(GLOBAL_STYLE)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Files are saved under the project's exports folder."))

        btn_row = QHBoxLayout()
        btn_specs = [
            ("Export books (CSV)", self._export_books, True),
            ("Export transactions (CSV)", self._export_trans, True),
            ("Export dashboard (TXT)", self._export_dash, True),
            ("Preview summary", self._preview, False),
        ]
        for text, slot, use_accent in btn_specs:
            b = QPushButton(text)
            if use_accent:
                b.setObjectName("accent")
            b.clicked.connect(slot)
            btn_row.addWidget(b)
        open_btn = QPushButton("Open exports folder")
        open_btn.clicked.connect(self._open_folder)
        btn_row.addWidget(open_btn)
        layout.addLayout(btn_row)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        layout.addWidget(self.text)

        box = QDialogButtonBox(QDialogButtonBox.Close)
        box.rejected.connect(self.reject)
        layout.addWidget(box)

    def _export_books(self):
        p = self.export_service.export_books_csv()
        QMessageBox.information(self, "Done", f"Saved to:\n{p}")

    def _export_trans(self):
        p = self.export_service.export_transactions_csv()
        QMessageBox.information(self, "Done", f"Saved to:\n{p}")

    def _export_dash(self):
        p = self.export_service.export_dashboard_txt(self.lib)
        QMessageBox.information(self, "Done", f"Saved to:\n{p}")

    def _preview(self):
        head = self.export_service.build_dashboard_text(self.lib)
        lines = [head, "", "--- Transactions (first 50) ---", ""]
        for t in self.lib.get_transactions()[:50]:
            st = "returned" if t.return_date else "on loan"
            lines.append(f"#{t.transaction_id}  {t.borrower}  \"{t.book_title}\"  {st}")
        self.text.setPlainText("\n".join(lines))

    def _open_folder(self):
        folder = default_export_dir()
        folder.mkdir(parents=True, exist_ok=True)
        p = str(folder.resolve())
        try:
            if sys.platform == "win32":
                os.startfile(p)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.run(["open", p], check=False)
            else:
                subprocess.run(["xdg-open", p], check=False)
        except Exception:
            QMessageBox.warning(self, "Notice", f"Open this folder manually:\n{p}")


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self, db, user: User, on_logout):
        super().__init__()
        self.db = db
        self.user = user
        self.on_logout = on_logout

        # Library / auth / export live here; this class only handles the UI.
        self.lib = Library(db)
        self.auth = Auth(db)
        self.export_service = ExportService(db)

        self.setWindowTitle("LBMS — Library Management System")
        self.setMinimumSize(1280, 760)
        self.setStyleSheet(GLOBAL_STYLE)

        self._build_ui()
        self.refresh_all()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ----- Top bar: right-side controls in one row, vertically centered -----
        topbar = QFrame()
        topbar.setFixedHeight(56)
        topbar.setStyleSheet(
            f"background-color: {PALETTE['surface']}; "
            f"border-bottom: 1px solid {PALETTE['border']};"
        )
        tb = QHBoxLayout(topbar)
        tb.setContentsMargins(24, 0, 24, 0)
        tb.setSpacing(0)

        brand = QLabel("📚  LBMS")
        brand.setStyleSheet(
            f"font-size: 18px; font-weight: 800; letter-spacing: 2px; color: {PALETTE['text']};"
            f" background: transparent;"
        )
        tb.addWidget(brand, 0, Qt.AlignmentFlag.AlignVCenter)
        tb.addStretch(1)

        top_right = QWidget()
        top_right.setStyleSheet("background: transparent;")
        tr = QHBoxLayout(top_right)
        tr.setContentsMargins(0, 0, 0, 0)
        tr.setSpacing(10)
        tr.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        users_btn = QPushButton("Users")
        users_btn.setObjectName("topbarAction")
        users_btn.setCursor(Qt.PointingHandCursor)
        users_btn.clicked.connect(self._open_users)
        tr.addWidget(users_btn, 0, Qt.AlignmentFlag.AlignVCenter)

        export_btn = QPushButton("Export")
        export_btn.setObjectName("topbarAction")
        export_btn.setCursor(Qt.PointingHandCursor)
        export_btn.clicked.connect(self._open_export)
        tr.addWidget(export_btn, 0, Qt.AlignmentFlag.AlignVCenter)

        self.user_badge = QLabel(f"  {self.user.username}  ")
        self.user_badge.setObjectName("userBadge")
        self.user_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tr.addWidget(self.user_badge, 0, Qt.AlignmentFlag.AlignVCenter)

        logout_btn = QPushButton("⏻  Logout")
        logout_btn.setObjectName("logout")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.clicked.connect(self._do_logout)
        tr.addWidget(logout_btn, 0, Qt.AlignmentFlag.AlignVCenter)

        tb.addWidget(top_right, 0, Qt.AlignmentFlag.AlignVCenter)

        root.addWidget(topbar)

        # ----- Main body -----
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(28, 24, 28, 24)
        body_layout.setSpacing(20)

        # Stats row
        stats_row = QHBoxLayout()
        stats_row.setSpacing(14)
        self.stat_total = StatCard("Total Books", "—", PALETTE["accent"])
        self.stat_available = StatCard("Available", "—", PALETTE["success"])
        self.stat_borrowed = StatCard("Borrowed", "—", PALETTE["warning"])
        self.stat_trans = StatCard("Transactions", "—", PALETTE["accent2"])
        for s in (self.stat_total, self.stat_available, self.stat_borrowed, self.stat_trans):
            stats_row.addWidget(s)
        body_layout.addLayout(stats_row)

        # Split: books | transactions (similar ratio to the original)
        split = QHBoxLayout()
        split.setSpacing(20)

        # --- Left: books ---
        books_frame = QFrame()
        books_frame.setObjectName("card")
        books_v = QVBoxLayout(books_frame)
        books_v.setContentsMargins(0, 0, 0, 0)
        books_v.setSpacing(0)

        bk_header = QWidget()
        bk_header_l = QHBoxLayout(bk_header)
        bk_header_l.setContentsMargins(16, 14, 16, 10)
        bk_title = QLabel("Books")
        bk_title.setObjectName("sectionTitle")
        bk_header_l.addWidget(bk_title)
        bk_header_l.addStretch()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍  Filter by title, author, genre…")
        self.search_box.setFixedWidth(260)
        self.search_box.textChanged.connect(self._filter_books)
        bk_header_l.addWidget(self.search_box)
        books_v.addWidget(bk_header)

        hdiv = QFrame()
        hdiv.setFrameShape(QFrame.HLine)
        hdiv.setStyleSheet(f"background: {PALETTE['border']}; max-height: 1px;")
        books_v.addWidget(hdiv)

        self.book_table = QTableWidget()
        self.book_table.setColumnCount(6)
        self.book_table.setHorizontalHeaderLabels(
            ["ID", "Title", "Author", "Genre", "Capacity", "Available"]
        )
        self.book_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.book_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.book_table.verticalHeader().setVisible(False)
        self.book_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.book_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.book_table.setShowGrid(False)
        self.book_table.setStyleSheet(
            self.book_table.styleSheet() + "QTableWidget { border: none; border-radius: 0; }"
        )
        books_v.addWidget(self.book_table)

        bk_btns = QWidget()
        bk_btns.setObjectName("panelFooter")
        bk_btn_l = QHBoxLayout(bk_btns)
        bk_btn_l.setContentsMargins(16, 10, 16, 10)
        bk_btn_l.setSpacing(10)
        add_bk = QPushButton("+ Add Book")
        add_bk.setObjectName("accent")
        upd_bk = QPushButton("✎  Update")
        del_bk = QPushButton("✕  Delete")
        del_bk.setObjectName("danger")
        ref_bk = QPushButton("↺  Refresh")
        add_bk.clicked.connect(self._add_book)
        upd_bk.clicked.connect(self._update_book)
        del_bk.clicked.connect(self._delete_book)
        ref_bk.clicked.connect(self.refresh_all)
        for b in (add_bk, upd_bk, del_bk, ref_bk):
            bk_btn_l.addWidget(b)
        bk_btn_l.addStretch()
        books_v.addWidget(bk_btns)

        split.addWidget(books_frame, 60)

        # --- Right: transactions ---
        trans_frame = QFrame()
        trans_frame.setObjectName("card")
        trans_v = QVBoxLayout(trans_frame)
        trans_v.setContentsMargins(0, 0, 0, 0)
        trans_v.setSpacing(0)

        tr_header = QWidget()
        tr_header_l = QHBoxLayout(tr_header)
        tr_header_l.setContentsMargins(16, 14, 16, 10)
        tr_title = QLabel("Transactions")
        tr_title.setObjectName("sectionTitle")
        tr_header_l.addWidget(tr_title)
        trans_v.addWidget(tr_header)

        tdiv = QFrame()
        tdiv.setFrameShape(QFrame.HLine)
        tdiv.setStyleSheet(f"background: {PALETTE['border']}; max-height: 1px;")
        trans_v.addWidget(tdiv)

        self.trans_table = QTableWidget()
        self.trans_table.setColumnCount(5)
        self.trans_table.setHorizontalHeaderLabels(
            ["ID", "Borrower", "Book Title", "Borrow Date", "Status"]
        )
        self.trans_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.trans_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.trans_table.verticalHeader().setVisible(False)
        self.trans_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.trans_table.setShowGrid(False)
        self.trans_table.setStyleSheet(
            self.trans_table.styleSheet() + "QTableWidget { border: none; border-radius: 0; }"
        )
        trans_v.addWidget(self.trans_table)

        tr_btns = QWidget()
        tr_btns.setObjectName("panelFooter")
        tr_btn_l = QHBoxLayout(tr_btns)
        tr_btn_l.setContentsMargins(16, 10, 16, 10)
        tr_btn_l.setSpacing(10)
        add_tr = QPushButton("+ Borrow")
        add_tr.setObjectName("accent")
        ret_tr = QPushButton("↩  Return")
        ret_tr.setObjectName("success")
        del_tr = QPushButton("✕  Delete")
        del_tr.setObjectName("danger")
        add_tr.clicked.connect(self._add_transaction)
        ret_tr.clicked.connect(self._return_book)
        del_tr.clicked.connect(self._delete_transaction)
        tr_btn_l.addWidget(add_tr)
        tr_btn_l.addWidget(ret_tr)
        tr_btn_l.addWidget(del_tr)
        tr_btn_l.addStretch()
        trans_v.addWidget(tr_btns)

        split.addWidget(trans_frame, 40)
        body_layout.addLayout(split)

        root.addWidget(body)

    # ----- Refresh after DB changes -----
    def refresh_all(self):
        self._load_books(self.search_box.text())
        self._load_transactions()
        self._update_stats()

    def _update_stats(self):
        books = self.lib.get_books()
        total = len(books)
        available = sum(b.available for b in books)
        borrowed = sum(b.capacity - b.available for b in books)
        trans = len(self.lib.get_transactions())
        self.stat_total.update_value(total)
        self.stat_available.update_value(available)
        self.stat_borrowed.update_value(borrowed)
        self.stat_trans.update_value(trans)

    def _load_books(self, filter_text=""):
        books = self.lib.get_books()
        ft = filter_text.lower()
        if ft:
            books = [
                b
                for b in books
                if ft in b.title.lower()
                or ft in b.author.lower()
                or ft in (b.genre or "").lower()
            ]
        self.book_table.setRowCount(len(books))
        for i, b in enumerate(books):
            vals = [b.book_id, b.title, b.author, b.genre or "—", b.capacity, b.available]
            for j, v in enumerate(vals):
                item = QTableWidgetItem(str(v))
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                if j == 5:
                    if b.available == 0:
                        item.setForeground(QColor(PALETTE["danger"]))
                    elif b.available < b.capacity:
                        item.setForeground(QColor(PALETTE["warning"]))
                    else:
                        item.setForeground(QColor(PALETTE["success"]))
                self.book_table.setItem(i, j, item)
        self.book_table.resizeRowsToContents()

    def _load_transactions(self):
        transactions = self.lib.get_transactions()
        self.trans_table.setRowCount(len(transactions))
        for i, t in enumerate(transactions):
            date_str = t.borrow_date.strftime("%Y-%m-%d %H:%M") if t.borrow_date else "—"
            returned = t.return_date is not None
            status = "Returned" if returned else "Borrowed"
            vals = [t.transaction_id, t.borrower, t.book_title, date_str, status]
            for j, v in enumerate(vals):
                item = QTableWidgetItem(str(v))
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                if j == 4:
                    item.setForeground(
                        QColor(PALETTE["success"] if returned else PALETTE["warning"])
                    )
                self.trans_table.setItem(i, j, item)
        self.trans_table.resizeRowsToContents()

    def _filter_books(self, text):
        self._load_books(text)

    # ----- Book actions -----
    def _add_book(self):
        dlg = BookDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return
        title, author, genre, capacity = dlg.get_data()
        if not title or not author:
            QMessageBox.warning(self, "Missing Fields", "Title and Author are required.")
            return
        self.lib.add_book(Book(title, author, genre, capacity))
        self.refresh_all()

    def _update_book(self):
        row = self.book_table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "No Selection", "Please select a book to update.")
            return
        book_id = int(self.book_table.item(row, 0).text())
        current_book = Book(
            title=self.book_table.item(row, 1).text(),
            author=self.book_table.item(row, 2).text(),
            genre=self.book_table.item(row, 3).text(),
            capacity=int(self.book_table.item(row, 4).text()),
        )
        dlg = BookDialog(self, book=current_book)
        if dlg.exec() != QDialog.Accepted:
            return
        title, author, genre, capacity = dlg.get_data()
        if not title or not author:
            QMessageBox.warning(self, "Missing Fields", "Title and Author are required.")
            return
        self.lib.update_book(book_id, title, author, genre, capacity)
        self.refresh_all()

    def _delete_book(self):
        row = self.book_table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "No Selection", "Please select a book to delete.")
            return
        title = self.book_table.item(row, 1).text()
        reply = QMessageBox.question(
            self, "Confirm Delete", f"Delete '{title}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            book_id = int(self.book_table.item(row, 0).text())
            self.lib.delete_book(book_id)
            self.refresh_all()

    # ----- Transaction actions -----
    def _add_transaction(self):
        books = self.lib.get_books()
        if not any(b.available > 0 for b in books):
            QMessageBox.information(self, "Borrow", "No available copies.")
            return
        dlg = BorrowDialog(self, books=books)
        if dlg.exec() != QDialog.Accepted:
            return
        borrower, book_id = dlg.get_data()
        if not borrower:
            QMessageBox.warning(self, "Missing Fields", "Borrower name is required.")
            return
        ok, msg = self.lib.borrow_book(borrower, book_id)
        if not ok:
            QMessageBox.warning(self, "Cannot Borrow", msg)
        self.refresh_all()

    def _return_book(self):
        row = self.trans_table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "No Selection", "Please select a transaction.")
            return
        if self.trans_table.item(row, 4).text() == "Returned":
            QMessageBox.information(self, "Already Returned", "Already returned.")
            return
        trans_id = int(self.trans_table.item(row, 0).text())
        borrower = self.trans_table.item(row, 1).text()
        book_title = self.trans_table.item(row, 2).text()
        reply = QMessageBox.question(
            self, "Confirm Return",
            f"Mark '{book_title}' as returned by {borrower}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            ok, msg = self.lib.return_book(trans_id)
            if not ok:
                QMessageBox.warning(self, "Error", msg)
            self.refresh_all()

    def _delete_transaction(self):
        row = self.trans_table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "No Selection", "Please select a transaction.")
            return
        trans_id = int(self.trans_table.item(row, 0).text())
        borrower = self.trans_table.item(row, 1).text()
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete transaction for '{borrower}'? Does NOT restore copies.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.lib.delete_transaction(trans_id)
            self.refresh_all()

    def _open_users(self):
        dlg = UserListDialog(self, self.auth, self.user.user_id)
        dlg.exec()

    def _open_export(self):
        dlg = ExportDataDialog(self, self.export_service, self.lib)
        dlg.exec()

    def _do_logout(self):
        reply = QMessageBox.question(
            self, "Logout", "Log out?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.close()
            self.on_logout()
