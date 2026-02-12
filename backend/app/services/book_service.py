import logging
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.schemas.books import BookCreate, BookUpdate
from app.models.books import Book
from app.models.user import User
from app.DAO.books_dao import BooksDAO
from app.core.cache import (
    get_books_list_cache,
    set_books_list_cache,
    invalidate_books_list_cache,
)
from app.core.db_errors import map_db_error

import math

logger = logging.getLogger("app.books")

async def create_book_service(db: AsyncSession, payload: BookCreate, current_user: User) -> Book:
    try:
        result = await db.execute(select(Book).where(Book.title == payload.title))
        existing_book = result.scalars().first()
        if existing_book:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title already use")
        book = Book(**payload.model_dump(), owner_id=current_user.id)
        db.add(book)
        await db.commit()
        await db.refresh(book)
        invalidate_books_list_cache(user_id=current_user.id)
        return book
    except Exception as e:
        print(f"errors from creating books {e}")
        raise


async def get_book_service(book_id: int, db: AsyncSession) -> Book:
    try:
        book = await db.get(Book, book_id)
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Title not found")
        return book
    except Exception as e:
        print(f"errors from get book {e}")
        raise


async def list_books_service(
    db: AsyncSession,
    current_user: User,
    title: str | None = None,
    author: str | None = None,
    sort_by: str | None = None,
    sort_dir: str = "desc",
    page: int = 1,
    page_size: int = 10,
):
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 10
    if page_size > 100:
        page_size = 100
    # normalize sort_dir
    sort_dir = sort_dir.lower()
    if sort_dir not in ("asc", "desc"):
        sort_dir = "desc"
    cached = get_books_list_cache(
        current_user,
        title,
        author,
        sort_by,
        sort_dir,
        page,
        page_size,
    )
    if cached is not None:
        return cached
    #print("error_spot", type(current_user))
    #cached = None
    #await db.execute("INVALID SQL")
    try:
        #await db.execute(text("SELECT * FROM table_that_does_not_exist"))
        items, total = await BooksDAO.list_by_owner_paginated(
            db,
            owner_id=current_user,
            title=title,
            author=author,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            page_size=page_size,
        )
    except Exception as exc:
        logger.exception("books.list.db_error", extra={"user_id": current_user})
        raise map_db_error(exc)
        

    total_pages = math.ceil(total / page_size) if total else 1
    result = {
        "items": items,
        "meta": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
    }
    set_books_list_cache(
        current_user,
        title,
        author,
        sort_by,
        sort_dir,
        page,
        page_size,
        result,
    )
    return result


async def update_book_service(db: AsyncSession, book_id: int, payload: BookUpdate, current_user: User) -> Book:
    try:
        book = await db.get(Book, book_id)
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
        if book.owner_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not alowed")
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(book, key, value)
        await db.commit()
        await db.refresh(book)
        invalidate_books_list_cache(user_id=current_user.id)
        return book
    except Exception as e:
        print(f"errors from updating book {e}")
        raise


async def delete_book_service(db: AsyncSession, book_id: int, current_user: User):
    try:
        book = await db.get(Book, book_id)
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
        if book.owner_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not alowed")
        await db.delete(book)
        await db.commit()
        invalidate_books_list_cache(user_id=current_user.id)
        return {"message": "Book deleted"}
    except Exception as e:
        print(f"errors from deleting book {e}")
        raise







