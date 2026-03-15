from datetime import datetime
from pydantic import BaseModel


class BorrowBookRequest(BaseModel):
    user_id: int


class BorrowRecordResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    status: str
    borrowed_at: datetime
    return_at: datetime | None = None

    class Config:
        from_attributes = True