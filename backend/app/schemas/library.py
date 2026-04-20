from pydantic import BaseModel, Field


class CreateBookWithLogIn(BaseModel):
    title: str = Field(..., min_length=2, max_length=80)
    description: str = Field(..., min_length=2, max_length=300)
    author: str = Field(..., min_length=2, max_length=50)
    category_id: int


class CreateBookWithLogOut(BaseModel):
    book_id: int
