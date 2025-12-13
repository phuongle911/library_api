from fastapi import APIRouter, Depends  #API library
from sqlalchemy.ext.asyncio import AsyncSession  #database library
from app.schemas.books import BookCreate, BookUpdate, BookResponse  #schemas/DTO layer
from app.core.database import get_db  #DB/engine layer
from app.services.book_service import (
    create_book_service,
    get_book_service,
    list_books_service,
    update_book_service,
    delete_book_service
    )  #service layer

book_router = APIRouter()


@book_router.post("/books", response_model=BookResponse)
async def create_book(payload: BookCreate, db: AsyncSession = Depends(get_db)):
    return await create_book_service(db, payload)


@book_router.get("/books/{book_id}", response_model=BookResponse)
async def get_book(book_id: int, db: AsyncSession = Depends(get_db)):
    return await get_book_service(book_id, db)


@book_router.get("/books", response_model=list[BookResponse])
async def list_books(
    db: AsyncSession = Depends(get_db),
    title: str | None = None,
    author: str | None = None,
    sort_by: str | None = None
):
    return await list_books_service(db=db, title=title, author=author, sort_by=sort_by)


@book_router.put("/books/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int,
    payload: BookUpdate,
    db: AsyncSession = Depends(get_db)
):
    return await update_book_service(db, book_id, payload)


@book_router.delete("/books/{book_id}")
async def delete_book(book_id: int, db: AsyncSession = Depends(get_db)):
    return await delete_book_service(db, book_id)
