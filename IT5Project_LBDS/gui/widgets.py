# -*- coding: utf-8 -*-
"""Small stat cards (four number tiles) used on the main dashboard."""
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from .styles import PALETTE


class StatCard(QFrame):
    def __init__(self, label: str, value: str, color: str | None = None):
        super().__init__()
        self.setObjectName("card")
        self.setMinimumHeight(88)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(4)

        val_lbl = QLabel(str(value))
        val_lbl.setObjectName("statValue")
        if color:
            val_lbl.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: 800;")
        self.value_label = val_lbl

        lbl = QLabel(label.upper())
        lbl.setObjectName("statLabel")

        layout.addWidget(val_lbl)
        layout.addWidget(lbl)

    def update_value(self, v) -> None:
        self.value_label.setText(str(v))
