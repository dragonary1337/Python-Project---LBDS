from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from auth import Auth
from db import Database
from .styles import LOGIN_STYLE, PALETTE

class LoginWindow(QMainWindow):
    """
    Sign-in screen: centered card with username and password.
    Uses top alignment in the outer layout so content is not squeezed vertically.
    """

    def __init__(self, db: Database, on_login_success):
        super().__init__()
        self.db = db
        self.auth = Auth(db)
        self.on_login_success = on_login_success

        self.setWindowTitle("LBMS — Sign In")
        self.setFixedSize(480, 620)
        self.setStyleSheet(LOGIN_STYLE)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        # Top + horizontal center: avoids vertical center squeezing the card.
        outer = QVBoxLayout(central)
        outer.setContentsMargins(24, 28, 24, 24)
        outer.setSpacing(16)

        card = QFrame()
        card.setObjectName("loginCard")
        card.setFixedWidth(400)

        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(14)
        card_layout.setContentsMargins(36, 40, 36, 36)

        # ----- Header -----
        brand = QLabel("📚")
        brand.setAlignment(Qt.AlignCenter)
        brand.setStyleSheet("font-size: 44px; background: transparent; border: none;")
        card_layout.addWidget(brand)

        app_name = QLabel("LBMS")
        app_name.setAlignment(Qt.AlignCenter)
        app_name.setStyleSheet(
            f"font-size: 28px; font-weight: 900; letter-spacing: 4px; "
            f"color: {PALETTE['text']}; background: transparent; border: none;"
        )
        card_layout.addWidget(app_name)

        subtitle = QLabel("Library Management System")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(
            f"font-size: 11px; color: {PALETTE['muted']}; letter-spacing: 2px; "
            f"background: transparent; border: none;"
        )
        card_layout.addWidget(subtitle)

        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setFixedHeight(1)
        div.setStyleSheet(f"background: {PALETTE['border']}; border: none;")
        card_layout.addWidget(div)
        card_layout.addSpacing(4)

        # ----- Fields -----
        self.username_field = QLineEdit()
        self.username_field.setPlaceholderText("Username")
        self.username_field.setMinimumHeight(46)
        card_layout.addWidget(self.username_field)

        self.password_field = QLineEdit()
        self.password_field.setPlaceholderText("Password")
        self.password_field.setEchoMode(QLineEdit.Password)
        self.password_field.setMinimumHeight(46)
        self.password_field.returnPressed.connect(self._do_login)
        card_layout.addWidget(self.password_field)

        # Error line: fixed height so layout stays stable when empty or when text wraps.
        self.error_lbl = QLabel("")
        self.error_lbl.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.error_lbl.setWordWrap(True)
        self.error_lbl.setMinimumHeight(40)
        self.error_lbl.setMaximumHeight(56)
        self.error_lbl.setStyleSheet(
            f"color: {PALETTE['danger']}; font-size: 12px; background: transparent; border: none;"
        )
        card_layout.addWidget(self.error_lbl)

        card_layout.addSpacing(6)

        # ----- Primary action -----
        login_btn = QPushButton("Sign In")
        login_btn.setObjectName("loginBtn")
        login_btn.setFixedHeight(50)
        login_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        login_btn.clicked.connect(self._do_login)
        card_layout.addWidget(login_btn)

        # Space before the register row so it does not visually merge with Sign In.
        card_layout.addSpacing(18)

        # ----- Register row (centered) -----
        reg_wrap = QWidget()
        reg_wrap.setStyleSheet("background: transparent;")
        reg_outer = QHBoxLayout(reg_wrap)
        reg_outer.setContentsMargins(0, 0, 0, 0)
        reg_outer.addStretch(1)
        reg_inner = QHBoxLayout()
        reg_inner.setSpacing(8)
        reg_lbl = QLabel("New here?")
        reg_lbl.setStyleSheet(
            f"color: {PALETTE['muted']}; font-size: 13px; background: transparent; border: none;"
        )
        reg_btn = QPushButton("Create account")
        reg_btn.setObjectName("registerBtn")
        reg_btn.setCursor(Qt.PointingHandCursor)
        reg_btn.setMinimumHeight(32)
        reg_btn.clicked.connect(self._do_register)
        reg_inner.addWidget(reg_lbl, 0, Qt.AlignVCenter)
        reg_inner.addWidget(reg_btn, 0, Qt.AlignVCenter)
        reg_outer.addLayout(reg_inner)
        reg_outer.addStretch(1)
        card_layout.addWidget(reg_wrap)

        outer.addWidget(card, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        footer = QLabel("Default: admin / admin123")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(
            f"color: {PALETTE['muted']}; font-size: 10px; background: transparent; border: none;"
        )
        outer.addWidget(footer, 0, Qt.AlignmentFlag.AlignHCenter)

        outer.addStretch(1)

    def _do_login(self):
        username = self.username_field.text().strip()
        password = self.password_field.text()
        user = self.auth.login(username, password)
        if user:
            self.on_login_success(user)
            self.close()
        else:
            self.error_lbl.setStyleSheet(
                f"color: {PALETTE['danger']}; font-size: 12px; background: transparent; border: none;"
            )
            self.error_lbl.setText("⚠  Invalid username or password")
            self.password_field.clear()
            self.password_field.setFocus()

    def _do_register(self):
        username = self.username_field.text().strip()
        password = self.password_field.text()
        if not username or not password:
            self.error_lbl.setStyleSheet(
                f"color: {PALETTE['danger']}; font-size: 12px; background: transparent; border: none;"
            )
            self.error_lbl.setText("⚠  Fill in both fields to register")
            return
        ok = self.auth.register(username, password)
        if ok:
            self.error_lbl.setStyleSheet(
                f"color: {PALETTE['success']}; font-size: 12px; background: transparent; border: none;"
            )
            self.error_lbl.setText("✓  Account created — you can now sign in")
        else:
            self.error_lbl.setStyleSheet(
                f"color: {PALETTE['danger']}; font-size: 12px; background: transparent; border: none;"
            )
            self.error_lbl.setText("⚠  Username already taken")
