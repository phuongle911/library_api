from dataclasses import dataclass
from datetime import datetime

@dataclass
class BookBorrowed:
    user_id: int
    book_id: int
    borrowed_at: datetime
