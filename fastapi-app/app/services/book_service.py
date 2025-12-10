from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import Depends
from fastapi import HTTPException, status
from app.schemas.books import BookCreate, BookUpdate
from app.models.books import Book
from app.core.database import get_db

async def create_book_service(db: AsyncSession, payload: BookCreate) -> Book:
   result = await db.execute(select(Book).where(Book.title == payload.title))
   existing_book = result.scalar_one_or_none()
   if existing_book:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title already use") 
   book = Book(**payload.model_dump())
   db.add(book)
   await db.commit()
   await db.refresh(book)
   return book

async def get_book_service(book_id: int, db: AsyncSession) -> Book:
   books = await db.get(Book, book_id)
   if not books:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Title not found")
   return books

async def list_books_service(
    db: AsyncSession,
    title: str | None = None,
    author:str | None = None, 
    sort_by: str | None = None
    ) -> Book:
    query = select(Book)

    #Apply filter if title provided
    if title:
        query = query.where(Book.title.ilike(f"%{title}%"))

    #Apply filter if title provided
    if author:
        query = query.where(Book.author.ilike(f"%{author}%"))

    #Apply sort_by for title
    if sort_by == "title":
        query = query.order_by(Book.title)
    elif sort_by == "author":
        query = query.order_by(Book.author)
    elif sort_by == "newest":
        query = query.order_by(Book.id.desc())
    elif sort_by == "oldest":
        query = query.order_by(Book.id.asc())

    result = await db.execute(query)
    books = result.scalars().all()
    if not books:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No book title")
    return books

async def update_book_service(db: AsyncSession, book_id: int, payload: BookUpdate) -> Book:
    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    for key, value in payload.model_dump().items():
        setattr(book, key, value)
    db.add(book)
    await db.commit()
    await db.refresh(book)
    return book

async def delete_book_service(db: AsyncSession, book_id: int) -> Book:
    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    await db.delete(book)
    await db.commit()
    return {"message": "Book deleted"}