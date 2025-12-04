from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.books import Book
from app.schemas.books import BookCreate, BookUpdate, BookResponse
from app.core.database import get_db

book_router = APIRouter()

@book_router.post("/books", response_model=BookResponse)
async def create_book(payload:BookCreate, db: AsyncSession = Depends(get_db)):
   result = await db.execute(select(Book).where(Book.title == payload.title))
   existing_book = result.scalar_one_or_none()
   if existing_book:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title already use") 
   book = Book(**payload.model_dump())
   db.add(book)
   await db.commit()
   await db.refresh(book)
   return book

@book_router.get("/books/{book_id}", response_model=BookResponse)
async def get_book(book_id: int, db: AsyncSession = Depends(get_db)):
   books = await db.get(Book, book_id)
   if not books:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Title not found")
   return books

@book_router.get("/books", response_model=list[BookResponse])
async def list_books(title: str | None = None, author:str | None = None, db: AsyncSession = Depends(get_db)):
    query = select(Book)

    #Apply filter if title provided
    if title:
        query = query.where(Book.title.ilike(f"%{title}%"))

    #Apply filter if title provided
    if author:
        query = query.where(Book.author.ilike(f"%{author}%"))


    result = await db.execute(query)
    books = result.scalars().all()
    if not books:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No book title")
    return books
 
@book_router.put("/books/{book_id}", response_model=BookResponse)
async def update_book(book_id: int, payload: BookUpdate, db: AsyncSession = Depends(get_db)):
    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    for key, value in payload.model_dump().items():
        setattr(book, key, value)
        db.add(book)
        await db.commit()
        await db.refresh(book)
        return book
    
@book_router.delete("/books/{book_id}")
async def delete_book(book_id: int, db: AsyncSession = Depends(get_db)):
    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    await db.delete(book)
    await db.commit()
    return {"message": "Book deleted"}


