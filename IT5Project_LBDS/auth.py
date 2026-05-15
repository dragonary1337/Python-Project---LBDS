from models import User


class Auth:
    def __init__(self, db):
        self.db = db
        self._seed_default_user()

    def _seed_default_user(self):
        """Create a default admin user if no users exist."""
        self.db.cursor.execute("SELECT COUNT(*) FROM users")
        count = self.db.cursor.fetchone()[0]
        if count == 0:
            self.db.cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                ("admin", "admin123")
            )
            self.db.commit()

    def login(self, username: str, password: str) -> User | None:
        """Return a User object if credentials are valid, else None."""
        self.db.cursor.execute(
            "SELECT id, username, password FROM users WHERE username=%s",
            (username,)
        )
        row = self.db.cursor.fetchone()
        if row and row[2] == password:
            return User(row[0], row[1], row[2])
        return None

    def register(self, username: str, password: str) -> bool:
        """Register a new user. Returns False if username already taken."""
        self.db.cursor.execute(
            "SELECT id FROM users WHERE username=%s", (username,)
        )
        if self.db.cursor.fetchone():
            return False
        self.db.cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, password)
        )
        self.db.commit()
        return True

    def list_users_public(self) -> list[tuple[int, str]]:
        """Return (id, username) for all users — no passwords."""
        self.db.cursor.execute(
            "SELECT id, username FROM users ORDER BY id"
        )
        return [(int(r[0]), str(r[1])) for r in self.db.cursor.fetchall()]

    def delete_user(self, target_id: int, requester_id: int) -> tuple[bool, str]:
        """Delete a user by id. Cannot delete yourself."""
        if target_id == requester_id:
            return False, "You cannot delete your own account while logged in."
        self.db.cursor.execute("SELECT id FROM users WHERE id=%s", (target_id,))
        if not self.db.cursor.fetchone():
            return False, "User not found."
        self.db.cursor.execute("DELETE FROM users WHERE id=%s", (target_id,))
        self.db.commit()
        return True, "User deleted."
