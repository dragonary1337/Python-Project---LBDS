# Light theme palette (soft background + blue primary)
PALETTE = {
    "bg": "#F0F4FA",  # window background
    "surface": "#FFFFFF",  # inputs / tables
    "card": "#FFFFFF",  # cards
    "border": "#D8DEE9",
    "accent": "#2563EB",  # primary
    "accent2": "#6366F1",
    "success": "#059669",
    "danger": "#DC2626",
    "warning": "#D97706",
    "text": "#0F172A",
    "muted": "#64748B",
    "hover": "#E8EEF9",  # hover for buttons / rows
    "header_bg": "#F1F5F9",  # table header
}

GLOBAL_STYLE = f"""
QWidget {{
    background-color: {PALETTE['bg']};
    color: {PALETTE['text']};
    font-family: 'Segoe UI', 'SF Pro Display', sans-serif;
    font-size: 13px;
}}

QMainWindow, QDialog {{
    background-color: {PALETTE['bg']};
}}

QPushButton {{
    background-color: {PALETTE['surface']};
    color: {PALETTE['text']};
    border: 1px solid {PALETTE['border']};
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: 500;
    min-height: 32px;
}}
QPushButton:hover {{
    background-color: {PALETTE['hover']};
    border-color: {PALETTE['accent']};
    color: {PALETTE['text']};
}}
QPushButton:pressed {{
    background-color: {PALETTE['accent']};
    border-color: {PALETTE['accent']};
    color: #ffffff;
}}

/* Primary actions: keep text visible even inside parents that set their own stylesheet */
QPushButton#accent {{
    background-color: {PALETTE['accent']};
    border: 1px solid {PALETTE['accent']};
    color: #ffffff;
    font-weight: 600;
}}
QPushButton#accent:hover {{
    background-color: #1D4ED8;
    border-color: #1D4ED8;
    color: #ffffff;
}}
QWidget#panelFooter QPushButton#accent {{
    background-color: {PALETTE['accent']};
    border: 1px solid {PALETTE['accent']};
    color: #ffffff;
}}
QWidget#panelFooter QPushButton#accent:hover {{
    background-color: #1D4ED8;
    border-color: #1D4ED8;
    color: #ffffff;
}}

QPushButton#danger {{
    background-color: #FEF2F2;
    border: 1px solid {PALETTE['danger']};
    color: {PALETTE['danger']};
}}
QPushButton#danger:hover {{
    background-color: {PALETTE['danger']};
    color: #ffffff;
}}

QPushButton#success {{
    background-color: #ECFDF5;
    border: 1px solid {PALETTE['success']};
    color: {PALETTE['success']};
}}
QPushButton#success:hover {{
    background-color: {PALETTE['success']};
    color: #ffffff;
}}

/* Top bar: same height for action buttons */
QPushButton#topbarAction {{
    background-color: {PALETTE['surface']};
    color: {PALETTE['text']};
    border: 1px solid {PALETTE['border']};
    border-radius: 8px;
    padding: 0 16px;
    min-height: 36px;
    max-height: 36px;
    font-size: 12px;
    font-weight: 600;
}}
QPushButton#topbarAction:hover {{
    background-color: {PALETTE['hover']};
    border-color: {PALETTE['accent']};
}}

QPushButton#logout {{
    background-color: {PALETTE['surface']};
    border: 1px solid {PALETTE['border']};
    color: {PALETTE['muted']};
    border-radius: 8px;
    padding: 0 14px;
    min-height: 36px;
    max-height: 36px;
    font-size: 12px;
    font-weight: 600;
}}
QPushButton#logout:hover {{
    border-color: {PALETTE['danger']};
    color: {PALETTE['danger']};
    background-color: #FEF2F2;
}}

QLineEdit, QSpinBox {{
    background-color: {PALETTE['surface']};
    border: 1px solid {PALETTE['border']};
    border-radius: 8px;
    padding: 8px 12px;
    color: {PALETTE['text']};
    font-size: 13px;
    selection-background-color: {PALETTE['accent']};
    selection-color: #ffffff;
}}
QLineEdit:focus, QSpinBox:focus {{
    border-color: {PALETTE['accent']};
    background-color: #FAFBFF;
}}
QLineEdit::placeholder {{
    color: {PALETTE['muted']};
}}

QTableWidget {{
    background-color: {PALETTE['surface']};
    border: 1px solid {PALETTE['border']};
    border-radius: 10px;
    gridline-color: {PALETTE['border']};
    selection-background-color: #DBEAFE;
    selection-color: {PALETTE['text']};
    outline: none;
}}
QTableWidget::item {{
    padding: 10px 14px;
    border-bottom: 1px solid {PALETTE['border']};
}}
QTableWidget::item:selected {{
    background-color: #DBEAFE;
    color: {PALETTE['text']};
}}
QHeaderView::section {{
    background-color: {PALETTE['header_bg']};
    color: {PALETTE['muted']};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 10px 14px;
    border: none;
    border-bottom: 1px solid {PALETTE['border']};
}}
QScrollBar:vertical {{
    background: {PALETTE['header_bg']};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {PALETTE['border']};
    border-radius: 4px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: {PALETTE['accent']};
}}
QScrollBar:horizontal {{
    height: 8px;
    background: {PALETTE['header_bg']};
}}
QScrollBar::handle:horizontal {{
    background: {PALETTE['border']};
    border-radius: 4px;
}}

QFrame#card {{
    background-color: {PALETTE['card']};
    border: 1px solid {PALETTE['border']};
    border-radius: 12px;
}}

/* Table card footers (avoid per-widget setStyleSheet on parents — it can break child button palettes) */
QWidget#panelFooter {{
    background-color: {PALETTE['surface']};
    border-top: 1px solid {PALETTE['border']};
}}

QLabel#sectionTitle {{
    color: {PALETTE['text']};
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 0.5px;
}}
QLabel#statValue {{
    color: {PALETTE['accent']};
    font-size: 28px;
    font-weight: 800;
}}
QLabel#statLabel {{
    color: {PALETTE['muted']};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}}
QLabel#userBadge {{
    color: {PALETTE['accent']};
    font-size: 12px;
    font-weight: 600;
    background-color: rgba(37, 99, 235, 0.08);
    border: 1px solid rgba(37, 99, 235, 0.22);
    border-radius: 20px;
    padding: 6px 14px;
}}

QTextEdit {{
    background-color: {PALETTE['surface']};
    border: 1px solid {PALETTE['border']};
    border-radius: 10px;
    padding: 10px;
    color: {PALETTE['text']};
}}

QDialog {{
    background-color: {PALETTE['bg']};
    border: 1px solid {PALETTE['border']};
    border-radius: 12px;
}}
QDialogButtonBox QPushButton {{
    min-width: 80px;
}}
QFormLayout QLabel {{
    color: {PALETTE['muted']};
    font-size: 12px;
    font-weight: 500;
}}
"""

LOGIN_STYLE = f"""
QWidget {{
    background-color: {PALETTE['bg']};
    color: {PALETTE['text']};
    font-family: 'Segoe UI', 'SF Pro Display', sans-serif;
}}
QFrame#loginCard {{
    background-color: {PALETTE['card']};
    border: 1px solid {PALETTE['border']};
    border-radius: 16px;
}}
QLineEdit {{
    background-color: {PALETTE['surface']};
    border: 1px solid {PALETTE['border']};
    border-radius: 10px;
    padding: 12px 16px;
    color: {PALETTE['text']};
    font-size: 14px;
}}
QLineEdit:focus {{
    border-color: {PALETTE['accent']};
    background-color: #FAFBFF;
}}
QPushButton#loginBtn {{
    background-color: {PALETTE['accent']};
    color: #ffffff;
    font-size: 14px;
    font-weight: 700;
    border: none;
    border-radius: 10px;
    padding: 12px;
    min-height: 46px;
}}
QPushButton#loginBtn:hover {{
    background-color: #1D4ED8;
}}
QPushButton#loginBtn:pressed {{
    background-color: #1E40AF;
}}
QPushButton#registerBtn {{
    background-color: transparent;
    color: {PALETTE['accent']};
    font-size: 13px;
    border: none;
    padding: 6px 8px;
    font-weight: 600;
}}
QPushButton#registerBtn:hover {{
    color: #1D4ED8;
    text-decoration: underline;
}}
"""
