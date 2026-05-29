import logging
from time import time
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from datetime import datetime, timezone

from app.domain.events.book_returned import BookReturned
from app.domain.events.dispatcher import dispatch_domain_event
from app.schemas.books import BookCreate, BookUpdate
from app.models.books import Book
from app.models.user import User
from app.DAO.books_dao import BooksDAO
from app.DAO.categories_dao import CategoriesDAO
from app.core.cache import (
    get_books_list_cache,
    set_books_list_cache,
    invalidate_books_list_cache,
)
from app.core.db_errors import map_db_error
from app.core.transactions import commit_or_rollback
from app.core.permissions import require_owner_or_admin

import math

logger = logging.getLogger("app.books")
BOOKS_LIST_CACHE = {}
CACHE_TTL_SECONDS = 30


def get_books_cache_key(page: int, page_size: int):
    return f"books:list:page={page}:size={page_size}"


def get_books_from_cache(key: str):
    cached = BOOKS_LIST_CACHE.get(key)
    if not cached:
        return None

    if cached["expires_at"] < time.time():
        BOOKS_LIST_CACHE.pop(key, None)
        return None
    return cached["data"]


def set_books_cache(key: str, data):
    BOOKS_LIST_CACHE[key] = {
        "data": data,
        "expires_at": time.time() + CACHE_TTL_SECONDS,
    }


def clear_books_cache():
    BOOKS_LIST_CACHE.clear()


async def create_book_service(
        db: AsyncSession,
        payload: BookCreate,
        current_user: User
        ) -> Book:

    category = await CategoriesDAO.get_by_id(db, payload.category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
            )

    existing_book = await BooksDAO.get_by_title(db, payload.title)
    if existing_book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book title already exists",
        )

    book = Book(
        title=payload.title,
        description=payload.description,
        author=payload.author,
        category_id=payload.category_id,
        owner_id=current_user.id,
        )

    try:
        created_book = await BooksDAO.create(db, book)
        invalidate_books_list_cache(user_id=current_user.id)
    except Exception as exc:
        logger.exception(
            "books.create.db_error %s",
            str(exc),
            # extra={"user_id": current_user},
        )
        raise map_db_error(exc)
    return created_book


async def get_book_service(book_id: int, db: AsyncSession, current_user: User) -> Book:
    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Title not found"
                )
    require_owner_or_admin(current_user, book.owner_id)
    return book


async def list_books_service(
    db: AsyncSession,
    current_user: int,
    title: str | None = None,
    author: str | None = None,
    category_id: int | None = None,
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
        category_id,
        sort_by,
        sort_dir,
        page,
        page_size,
    )
    if cached is not None:
        return cached
    # cached = None
    # await db.execute("INVALID SQL")
    try:
        # await db.execute(text("SELECT * FROM table_that_does_not_exist"))
        items, total = await BooksDAO.list_by_owner_paginated(
            db,
            owner_id=current_user,
            title=title,
            author=author,
            category_id=category_id,
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
        category_id,
        sort_by,
        sort_dir,
        page,
        page_size,
        result,
    )
    return result


async def update_book_service(
        db: AsyncSession,
        book_id: int,
        payload: BookUpdate,
        current_user: User
        ) -> Book:
    try:
        book = await db.get(Book, book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
                )
        require_owner_or_admin(current_user, book.owner_id)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(book, key, value)
        await commit_or_rollback(db)
        await db.refresh(book)
        invalidate_books_list_cache(user_id=current_user.id)
        return book
    except Exception as exc:
        logger.exception("books.update.error", extra={"book_id": book_id}, exc_info=exc)
        raise


async def delete_book_service(db: AsyncSession, book_id: int, current_user: User):
    try:
        book = await db.get(Book, book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
                )
        require_owner_or_admin(current_user, book.owner_id)
        await db.delete(book)
        await commit_or_rollback(db)
        invalidate_books_list_cache(user_id=current_user.id)
        return {"message": "Book deleted"}
    except Exception as exc:
        logger.exception("books.delete.error", extra={"book_id": book_id}, exc_info=exc)
        raise
