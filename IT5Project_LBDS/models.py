from datetime import datetime


class User:
    def __init__(self, user_id, username, password):
        self.user_id = user_id
        self.username = username
        self.password = password

    def display_info(self):
        return f"[{self.user_id}] {self.username}"


class Book:
    def __init__(self, title, author, genre, capacity,
                available=True, book_id=None):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.genre = genre
        self.capacity = capacity          # total copies
        self.available = available        # copies currently available

    def display_info(self):
        status = f"{self.available}/{self.capacity} available"
        return f"[{self.book_id}] {self.title} — {self.author} ({status})"


class Transaction:
    def __init__(self, transaction_id, borrower, book_title,
                borrow_date=None, return_date=None):
        self.transaction_id = transaction_id
        self.borrower = borrower
        self.book_title = book_title
        self.borrow_date = borrow_date or datetime.now()
        self.return_date = return_date

    def display_info(self):
        return (f"[{self.transaction_id}] {self.borrower} borrowed '{self.book_title}' "
                f"on {self.borrow_date}")