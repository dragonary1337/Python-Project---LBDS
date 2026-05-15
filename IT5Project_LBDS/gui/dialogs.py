# -*- coding: utf-8 -*-
"""Modal dialogs for adding/editing books and borrowing; opened from the main window."""
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QHBoxLayout,
)
from PySide6.QtCore import Qt

from .styles import GLOBAL_STYLE, PALETTE
from models import Book


class BookDialog(QDialog):
    def __init__(self, parent=None, book: Book | None = None):
        super().__init__(parent)
        self.setWindowTitle("Book Details")
        self.setMinimumWidth(400)
        self.setStyleSheet(GLOBAL_STYLE)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(28, 28, 28, 28)

        title_lbl = QLabel("📖  " + ("Edit Book" if book else "New Book"))
        title_lbl.setObjectName("sectionTitle")
        layout.addWidget(title_lbl)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        self.title_edit = QLineEdit(book.title if book else "")
        self.title_edit.setPlaceholderText("e.g. The Great Gatsby")
        self.author_edit = QLineEdit(book.author if book else "")
        self.author_edit.setPlaceholderText("e.g. F. Scott Fitzgerald")
        self.genre_edit = QLineEdit(book.genre if book else "")
        self.genre_edit.setPlaceholderText("e.g. Classic Fiction")
        self.capacity_slider = QSlider(Qt.Horizontal)
        self.capacity_slider.setMinimum(0)
        max_capacity = book.capacity if book else 100
        self.capacity_slider.setMaximum(max_capacity)
        self.capacity_slider.setValue(book.capacity if book else 1)
        
        self.capacity_value_lbl = QLabel(str(book.capacity if book else 1))
        self.capacity_value_lbl.setMinimumWidth(30)
        self.capacity_slider.valueChanged.connect(
            lambda v: self.capacity_value_lbl.setText(str(v))
        )
        
        capacity_row = QHBoxLayout()
        capacity_row.addWidget(self.capacity_slider)
        capacity_row.addWidget(self.capacity_value_lbl)

        form.addRow("Title", self.title_edit)
        form.addRow("Author", self.author_edit)
        form.addRow("Genre", self.genre_edit)
        form.addRow("Capacity", capacity_row)
        layout.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        ok_btn = btns.button(QDialogButtonBox.Ok)
        ok_btn.setObjectName("accent")
        ok_btn.setText("Save")
        layout.addWidget(btns)

    def get_data(self):
        return (
            self.title_edit.text().strip(),
            self.author_edit.text().strip(),
            self.genre_edit.text().strip(),
            self.capacity_slider.value(),
        )


class BorrowDialog(QDialog):
    def __init__(self, parent=None, books=None):
        super().__init__(parent)
        self.books = books or []
        self.setWindowTitle("Borrow a Book")
        self.setMinimumWidth(420)
        self.setStyleSheet(GLOBAL_STYLE)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(28, 28, 28, 28)

        title_lbl = QLabel("🔁  Borrow a Book")
        title_lbl.setObjectName("sectionTitle")
        layout.addWidget(title_lbl)

        form = QFormLayout()
        form.setSpacing(12)

        self.borrower_edit = QLineEdit()
        self.borrower_edit.setPlaceholderText("Borrower's full name")

        self.book_id_spin = QSpinBox()
        available_ids = [b.book_id for b in self.books if b.available > 0 and b.book_id is not None]
        if available_ids:
            self.book_id_spin.setMinimum(min(available_ids))
            self.book_id_spin.setMaximum(max(available_ids))
            self.book_id_spin.setValue(available_ids[0])
        else:
            self.book_id_spin.setMinimum(0)
            self.book_id_spin.setMaximum(0)
            self.book_id_spin.setValue(0)
        self.book_id_spin.valueChanged.connect(self._update_preview)

        self.capacity_slider = QSlider(Qt.Horizontal)
        self.capacity_slider.setMinimum(0)
        self.capacity_slider.setMaximum(1)
        self.capacity_slider.setValue(1)
        
        self.capacity_value_lbl = QLabel("1")
        self.capacity_value_lbl.setMinimumWidth(30)
        self.capacity_slider.valueChanged.connect(
            lambda v: self.capacity_value_lbl.setText(str(v))
        )
        
        capacity_row = QHBoxLayout()
        capacity_row.addWidget(self.capacity_slider)
        capacity_row.addWidget(self.capacity_value_lbl)

        self.preview_lbl = QLabel("")
        self.preview_lbl.setStyleSheet(
            f"color: {PALETTE['muted']}; font-size: 12px; background: transparent; border: none;"
        )

        form.addRow("Borrower", self.borrower_edit)
        form.addRow("Book ID", self.book_id_spin)
        form.addRow("Quantity", capacity_row)
        form.addRow("", self.preview_lbl)
        layout.addLayout(form)

        self._update_preview(self.book_id_spin.value())

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        ok_btn = btns.button(QDialogButtonBox.Ok)
        ok_btn.setObjectName("accent")
        ok_btn.setText("Borrow")
        layout.addWidget(btns)

    def _update_preview(self, book_id):
        book = next((b for b in self.books if b.book_id == book_id), None)
        if book:
            avail_color = PALETTE["success"] if book.available > 0 else PALETTE["danger"]
            self.preview_lbl.setText(
                f'<span style="color:{PALETTE["text"]}">{book.title}</span>'
                f' &nbsp;&middot;&nbsp; '
                f'<span style="color:{avail_color}">{book.available}/{book.capacity} available</span>'
            )
            
            self.capacity_slider.setMaximum(max(1, book.available))
            self.capacity_slider.setValue(min(1, book.available))
        else:
            self.preview_lbl.setText(
                f'<span style="color:{PALETTE["danger"]}">Book ID not found or no copies</span>'
            )
            self.capacity_slider.setMaximum(1)
            self.capacity_slider.setValue(0)

    def get_data(self):
        return self.borrower_edit.text().strip(), self.book_id_spin.value(), self.capacity_slider.value()
