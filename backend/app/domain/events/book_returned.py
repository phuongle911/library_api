from dataclasses import dataclass
from datetime import datetime


@dataclass
class BookReturned:
    user_id: int
    book_id: int
    borrow_record_id: int
    returned_at: datetime