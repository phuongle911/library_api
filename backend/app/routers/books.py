from fastapi import APIRouter, Depends, Query   #API library
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
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import PaginatedResponse, BookOut

book_router = APIRouter()


@book_router.post("/books", response_model=BookResponse, status_code=201)
async def create_book(payload: BookCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await create_book_service(db, payload, current_user)


@book_router.get("/books/{book_id}", response_model=BookResponse, status_code=200)
async def get_book(book_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await get_book_service(book_id, db)


@book_router.get("/books", response_model=PaginatedResponse[BookOut])
async def list_books(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at"), 
    sort_dir: str = Query("decs"), 
    db: AsyncSession = Depends(get_db),
    ):
    return await list_books_service(db, page, page_size, sort_by, sort_dir)


@book_router.put("/books/{book_id}", response_model=BookResponse, status_code=200)
async def update_book(
    book_id: int,
    payload: BookUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await update_book_service(db, book_id, payload, current_user)


@book_router.delete("/books/{book_id}", status_code=204)
async def delete_book(book_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await delete_book_service(db, book_id, current_user)
