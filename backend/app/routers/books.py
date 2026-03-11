import logging
from fastapi import APIRouter, Depends, Query, Request   #API library
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
from app.core.decorator.logging import log_route
from app.schemas.books import BookListResponse

logger = logging.getLogger("app.books")

book_router = APIRouter()


@book_router.post("/books", response_model=BookResponse, status_code=201)
async def create_book(payload: BookCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await create_book_service(db, payload, current_user)


@book_router.get("/books/{book_id}", response_model=BookResponse, status_code=200)
async def get_book(book_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await get_book_service(book_id, db)


@book_router.get("/books", response_model=list[BookListResponse])
#@log_route
async def list_books(
    title: str | None = Query(default=None),
    author: str | None = Query(default=None),
    category_id: int | None = Query(default=None),
    sort_by: str | None = Query(default=None),
    sort_dir: str = Query(default="desc"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ):
    print(f"error splot {current_user.id}")
    # logger.info(
    #     "books.list",
    #     extra={
    #         "request_id": request.state.request_id,
    #         "page": page,
    #         "page_size": page_size,
    #         "sort_by": sort_by,
    #         "sort_dir": sort_dir,
    #     },
    # )
    return await list_books_service(
        db=db, 
        current_user=current_user.id,
        title=title,
        author=author,
        category_id=category_id,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        page_size=page_size,
        )


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
