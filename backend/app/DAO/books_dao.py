from sqlalchemy import select
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
    async def list_by_owner(
        db: AsyncSession,
        owner_id: int | None =None,
        title: str | None = None,
        author: str | None = None,
        sort_by:str | None = None,
    ) -> list[Book]:
        print("DAO list() called")
        
        query = select(Book).where(Book.owner_id == owner_id)

        if title:
            query = query.where(Book.title.ilike(f"%{title}%"))

        if author:
            query = query.where(Book.author.ilke(f"%{author}%%"))
            
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
    async def create(db: AsyncSession, payload:BookCreate, owner_id:int) -> Book:
        book = Book(**payload.model_dump(), owner_id = owner_id)
        db.add(book)
        await db.commit()
        await db.refresh(book)
        return book
    
    @staticmethod
    async def update(db: AsyncSession, book: Book, payload: BookUpdate) -> Book:
        for key, value in payload.model_dump(execute_unset=True).items():
            setattr(book, key, value)
            await db.commit()
            await db.refresh(book)
            return book
        
    @staticmethod
    async def delete(db: AsyncSession, book: Book) -> None:
        await db.delete(book)
        await db.commit()