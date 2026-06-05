from pydantic import BaseModel


class BookResponse(BaseModel):
    id: int
    title: str
    available_copies: int
