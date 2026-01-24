from pydantic import BaseModel
from typing import Generic, List, TypeVar
from datetime import datetime

T = TypeVar("T")

class PageMeta(BaseModel):
    page: int
    page_size: int
    total:int
    total_pages:int
    has_next: bool
    has_prev: bool

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    meta: PageMeta

class BookOut(BaseModel):
    id: int
    title: str
    author: str
    created_at: datetime

    class Congfig:
        from_attributes = True