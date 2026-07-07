from datetime import datetime
from pydantic import BaseModel


class ReservationCreateRequest(BaseModel):
    book_id: int


class ReservationResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    status: str
    created_at: datetime
    fulfilled_at: datetime | None = None
    cancelled_at: datetime | None = None

    class Config:
        from_attributes = True
