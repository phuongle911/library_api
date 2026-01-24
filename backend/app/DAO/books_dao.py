from sqlalchemy import select, func, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.books import Book
from app.schemas.books import BookCreate, BookUpdate

class BooksDAO:
    
    @staticmethod
    async def get_by_id(db: AsyncSession, book_id: int) -> Book | None:
        return await db.get(Book, book_id)
    
    @staticmethod
    async def get_by_title(db: AsyncSession, title: str) -> Book | None:
        result = await db.execute(select(Book).where(Book.title == title))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_by_owner_paginated(
        db: AsyncSession,
        owner_id: int,
        title: str | None = None,
        author: str | None = None,
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
            .where(*filters)
            .order_by(order_expr)
            .offset(offset)
            .limit(page_size)
        )
        result = await db.execute(data_query)
        items = result.scalars().all()
        return items, total
    
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
    async def create(db: AsyncSession, payload: BookCreate, owner_id: int) -> Book:
        book = Book(**payload.model_dump(), owner_id=owner_id)
        db.add(book)
        await db.commit()
        await db.refresh(book)
        return book
    
    @staticmethod
    async def update(db: AsyncSession, book: Book, payload: BookUpdate) -> Book:
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(book, key, value)
        await db.commit()
        await db.refresh(book)
        return book
    
    @staticmethod
    async def delete(db: AsyncSession, book: Book) -> None:
        await db.delete(book)
        await db.commit()