from datetime import datetime
from models import Book, Transaction


class Library:
    def __init__(self, db):
        self.db = db

    # ──────────────── BOOKS ────────────────
    def add_book(self, book: Book):
        self.db.cursor.execute("""
            INSERT INTO books (title, author, genre, capacity, available)
            VALUES (%s, %s, %s, %s, %s)
        """, (book.title, book.author, book.genre, book.capacity, book.capacity))
        self.db.commit()

    def get_books(self) -> list[Book]:
        self.db.cursor.execute("SELECT id, title, author, genre, capacity, available FROM books")
        rows = self.db.cursor.fetchall()
        return [Book(r[1], r[2], r[3], r[4], r[5], r[0]) for r in rows]

    def update_book(self, book_id, title, author, genre, capacity):
        self.db.cursor.execute("""
            UPDATE books SET title=%s, author=%s, genre=%s, capacity=%s
            WHERE id=%s
        """, (title, author, genre, capacity, book_id))
        self.db.commit()

    def delete_book(self, book_id):
        self.db.cursor.execute("DELETE FROM books WHERE id=%s", (book_id,))
        self.db.commit()

    # ──────────────── TRANSACTIONS ────────────────
    def get_transactions(self) -> list[Transaction]:
        self.db.cursor.execute("SELECT * FROM transactions")
        rows = self.db.cursor.fetchall()
        return [Transaction(r[0], r[1], r[2], r[3], r[4]) for r in rows]

    def borrow_book(self, borrower: str, book_id: int) -> tuple[bool, str]:
        """
        Create a transaction and decrement available copies.
        Returns (success, message).
        """
        self.db.cursor.execute(
            "SELECT title, available FROM books WHERE id=%s", (book_id,)
        )
        row = self.db.cursor.fetchone()
        if not row:
            return False, "Book not found."
        title, avail = row
        if avail <= 0:
            return False, f"No copies of '{title}' are currently available."

        # Decrement available
        self.db.cursor.execute(
            "UPDATE books SET available = available - 1 WHERE id=%s", (book_id,)
        )
        # Record transaction (return_date NULL = still borrowed)
        self.db.cursor.execute("""
            INSERT INTO transactions (borrower, book_title, borrow_date, return_date)
            VALUES (%s, %s, %s, NULL)
        """, (borrower, title, datetime.now()))
        self.db.commit()
        return True, f"'{title}' borrowed by {borrower}."

    def return_book(self, trans_id: int) -> tuple[bool, str]:
        """
        Mark a transaction as returned and increment available copies.
        Returns (success, message).
        """
        self.db.cursor.execute(
            "SELECT borrower, book_title, return_date FROM transactions WHERE id=%s",
            (trans_id,)
        )
        row = self.db.cursor.fetchone()
        if not row:
            return False, "Transaction not found."
        borrower, book_title, return_date = row
        if return_date is not None:
            return False, "This book has already been returned."

        # Mark returned
        self.db.cursor.execute("""
            UPDATE transactions SET return_date=%s WHERE id=%s
        """, (datetime.now(), trans_id))

        # Increment available (cap at capacity)
        self.db.cursor.execute("""
            UPDATE books
            SET available = LEAST(available + 1, capacity)
            WHERE title=%s
        """, (book_title,))
        self.db.commit()
        return True, f"'{book_title}' returned by {borrower}."

    def delete_transaction(self, trans_id: int):
        self.db.cursor.execute(
            "DELETE FROM transactions WHERE id=%s", (trans_id,)
        )
        self.db.commit()