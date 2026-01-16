from sqlalchemy.ext.asyncio import AsyncSession  #database library
from sqlalchemy.future import select  #database library
from fastapi import HTTPException, status  #API library
from app.schemas.books import BookCreate, BookUpdate  #schemas/DTO layer
from app.models.books import Book  #models/ORM layer
from app.models.user import User  #models/ORM layer
from functools import lru_cache  #caching library
from app.core.cache import(
    get_books_list_cache,
    set_books_list_cache,
    invalidate_books_list_cache,
)


@lru_cache(maxsize=128)
def _cached_list_books(title: str | None, author: str | None, sort_by: str | None):
    return (title, author, sort_by)
async def create_book_service(db: AsyncSession, payload: BookCreate, current_user: User) -> Book:
   try:
        invalidate_books_list_cache()
        result = await db.execute(select(Book).where(Book.title == payload.title))
        existing_book = result.scalar_one_or_none()
        if existing_book:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title already use") 
        book = Book(**payload.model_dump(), owner_id=current_user.id)
        db.add(book)
        await db.commit()
        await db.refresh(book)
        return book
   except Exception as e:
       print(f"errors from creating books {e}")
       return e


async def get_book_service(book_id: int, db: AsyncSession) -> Book:
   try:
        books = await db.get(Book, book_id)
        if not books:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Title not found")
        return books
   except Exception as e:
         print(f"errors from get book {e}")
         return e       
   

async def list_books_service(
    db: AsyncSession,
    title: str | None = None,
    author:str | None = None, 
    sort_by: str | None = None
    ) -> Book:
    try:
            cached = get_books_list_cache(title, author, sort_by)
            if cached is not None:
                return cached
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
            print("HITTING DATABASE")

            result = await db.execute(query)
            books = result.scalars().all()
            if not books:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No book title")
            set_books_list_cache(title, author, sort_by, books)
            return books
    except Exception as e:
        print(f"errors from get list books {e}")
        return e    


async def update_book_service(db: AsyncSession, book_id: int, payload: BookUpdate, current_user:User) -> Book:
    try:
            invalidate_books_list_cache()
            book = await db.get(Book, book_id)
            if not book:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
            if book.owner_id != current_user.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not alowed")
            for key, value in payload.model_dump().items():
                setattr(book, key, value)
            db.add(book)
            await db.commit()
            await db.refresh(book)
            return book
    except Exception as e:
            print(f"errors from updating book {e}")
            return e    
    
    
async def delete_book_service(db: AsyncSession, book_id: int, current_user:User) -> Book:
    try:
            invalidate_books_list_cache()
            book = await db.get(Book, book_id)
            if not book:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
            if book.owner_id != current_user.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not alowed")
            await db.delete(book)
            await db.commit()
            return {"message": "Book deleted"}
    except Exception as e:
            print(f"errors from deleting book {e}")
            return e    