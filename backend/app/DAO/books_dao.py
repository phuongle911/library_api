from sqlalchemy import select, func, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import selectinload

from app.models.books import Book
from app.schemas.books import BookUpdate
from app.core.decorator.retry import retry_async
from app.core.transactions import commit_or_rollback
from app.schemas.books import BookCreate, BookUpdate


class BooksDAO:
    @staticmethod
    async def get_by_title(db: AsyncSession, title: str) -> Book | None:
        result = await db.execute(select(Book).where(Book.title == title))
        return result.scalar_one_or_none()

    @retry_async(attempts=3, delay_seconds=0.2, exceptions=(OperationalError,))
    @staticmethod
    async def list_by_owner_paginated(
        db: AsyncSession,
        owner_id: int,
        title: str | None = None,
        author: str | None = None,
        category_id: int | None = None,
        sort_by: str | None = None,
        sort_dir: str = "desc",
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[Book], int]:
        print("DAO list_by_owner_paginated() called")
        filters = [Book.owner_id == owner_id]
        if title:
            filters.append(Book.title.ilike(f"%{title}%"))
        if author:
            filters.append(Book.author.ilike(f"%{author}%"))
        if category_id:
            filters.append(Book.category_id == category_id)
        total_query = select(func.count(Book.id)).where(*filters)
        total = (await db.execute(total_query)).scalar_one()
        if sort_by == "title":
            sort_col = Book.title
        elif sort_by == "author":
            sort_col = Book.author
        else:
            sort_col = Book.id
        order_expr = desc(sort_col) if sort_dir == "desc" else asc(sort_col)
        offset = (page - 1) * page_size
        data_query = (
            select(Book)
            .options(selectinload(Book.category))
            .where(*filters)
            .order_by(order_expr)
            .offset(offset)
            .limit(page_size)
        )
        result = await db.execute(data_query)
        items = result.scalars().all()
        return items, total

    @retry_async(attempts=3, delay_seconds=0.2, exceptions=(OperationalError,))
    @staticmethod
    async def list_by_owner(
        db: AsyncSession,
        owner_id: int | None = None,
        title: str | None = None,
        author: str | None = None,
        sort_by: str | None = None,
    ) -> list[Book]:
        print("DAO list_by_owner() called")
        query = select(Book).where(Book.owner_id == owner_id)
        if title:
            query = query.where(Book.title.ilike(f"%{title}%"))
        if author:
            query = query.where(Book.author.ilike(f"%{author}%"))
        if sort_by == "title":
            query = query.order_by(Book.title)
        elif sort_by == "author":
            query = query.order_by(Book.author)
        elif sort_by == "newest":
            query = query.order_by(Book.id.desc())
        elif sort_by == "oldest":
            query = query.order_by(Book.id.asc())
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def create(
        db: AsyncSession,
        payload: Book | BookCreate,
        owner_id: int | None = None,
    ) -> Book:
        if isinstance(payload, Book):
            book = payload
        else:
            if owner_id is None:
                raise ValueError("owner_id is required when creating from BookCreate")
            book = Book(
                title=payload.title,
                description=payload.description,
                author=payload.author,
                category_id=payload.category_id,
                owner_id=owner_id,
            )
        db.add(book)
        await commit_or_rollback(db)
        await db.refresh(book)
        return book

    @staticmethod
    async def update(db: AsyncSession, book: Book, payload: BookUpdate) -> Book:
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(book, key, value)
        await commit_or_rollback(db)
        await db.refresh(book)
        return book

    @staticmethod
    async def delete(db: AsyncSession, book: Book) -> None:
        await db.delete(book)
        await commit_or_rollback(db)

    @staticmethod
    async def list_with_category(
        db: AsyncSession,
        title: str | None = None,
        category_id: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Book]:
        query = select(Book).options(selectinload(Book.category))

        if title:
            query = query.where(Book.title.ilike(f"%{title}%"))

        if category_id:
            query = query.order_by(Book.id.desc()).limit(limit).offset(offset)

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, book_id: int) -> Book | None:
        result = await db.execute(
            select(Book).where(Book.id == book_id)
        )
        return result.scalars().first()

    @staticmethod
    async def get_by_id_for_update(db: AsyncSession, book_id: int) -> Book | None:
        result = await db.execute(
            select(Book)
            .where(Book.id == book_id)
            .with_for_update()
        )
        return result.scalars().first()
