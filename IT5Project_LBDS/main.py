"""Application entry: connect to the database, show login, then main window after sign-in."""
import sys
from PySide6.QtWidgets import QApplication
from db import Database
from gui import LoginWindow, MainWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    db = Database()

    # Keep window references so they are not garbage-collected and disappear.
    windows = {}

    def open_main(user):
        def logout():
            windows["main"].deleteLater()
            del windows["main"]
            open_login()

        win = MainWindow(db, user, on_logout=logout)
        windows["main"] = win
        win.show()

    def open_login():
        win = LoginWindow(db, on_login_success=open_main)
        windows["login"] = win
        win.show()

    open_login()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
