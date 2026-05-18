from fastapi import APIRouter, Depends, HTTPException, logger, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.library import CreateBookWithLogIn, CreateBookWithLogOut
from app.services.library_service import LibraryService
from app.schemas.books import BookCreate
from app.core.dependencies import get_current_user
from app.models.user import User
from app.DAO.categories_dao import CategoriesDAO

library_router = APIRouter(prefix="/library", tags=["Library"])
service = LibraryService()


@library_router.post("/books", response_model=CreateBookWithLogOut)
async def create_book_with_log(
    payload: CreateBookWithLogIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
      ):
    try:
        category = await CategoriesDAO.get_by_id(db, payload.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )
        data = BookCreate(
            title=payload.title,
            description=payload.description,
            author=payload.author,
            category_id=payload.category_id,
            )
        book = await service.create_book_with_log(
            db=db,
            data=data,
            owner_id=current_user.id)
        return {"book_id": book.id}
    except Exception as exc:
        logger.exception(
            "library.create_book_with_log.error %s", exc,
            extra={"user_id": current_user.id},
        )
