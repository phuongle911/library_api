from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.DAO.users_dao import UsersDAO
from app.DAO.books_dao import BooksDAO
from app.DAO.borrow_records_dao import BorrowRecordsDAO
from app.models.borrow_record import BorrowRecord


async def borrow_book_service(
        db: AsyncSession,
        book_id: int,
        user_id: int,
):
    async with db.begin():
        user = await UsersDAO.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404, 
                detail="User not found",
            )
        book = await BooksDAO.get_by_id(db, book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404, 
                detail="Book not found",
            )
        active_borrow = await BorrowRecordsDAO.get_active_by_user_and_book(
            db=db,
            user_id=user_id,
            book_id=book_id,
        )
        if active_borrow:
            raise HTTPException(
                status_code=400,
                detail="User already has this book borrowed",
            )
        
        if book.available_copies <= 0:
            raise HTTPException(
                status_code=status.HTTP_400, 
                detail="No available copies left",
            )
        
        book.available_copies -= 1

        borrow_record = await BorrowRecordsDAO.create(
            db=db,
            user_id=user_id,
            book_id=book_id,
        )

        await db.refresh(borrow_record)
        return borrow_record
    

async def get_active_borrows_service(db: AsyncSession):
    return await BorrowRecordsDAO.get_active(db)


async def get_borrow_history_service(db: AsyncSession):
    return await BorrowRecordsDAO.get_history(db)


async def get_user_borrow_history_service(db: AsyncSession, user_id: int):
    return await BorrowRecordsDAO.get_user_history(db, user_id)


async def get_book_borrow_history_service(db: AsyncSession, book_id: int):
    return await BorrowRecordsDAO.get_book_history(db, book_id)