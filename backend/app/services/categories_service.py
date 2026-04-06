from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.DAO.categories_dao import CategoriesDAO
from app.models.categories import Category
from app.schemas.categories import CategoryCreate, CategoryUpdate


async def create_category_service(
        db: AsyncSession,
        payload: CategoryCreate
        ) -> Category:
    existing_category = await CategoriesDAO.get_by_name(db, payload.name)
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
            )

    return await CategoriesDAO.create(db, payload.model_dump())


async def get_category_by_id_service(db: AsyncSession, category_id: int) -> Category:
    category = await CategoriesDAO.get_by_id(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
            )
    return category


async def list_categories_service(
        db: AsyncSession,
        name: str | None = None,
        limit: int = 50,
        offset: int = 0,
        ) -> list[Category]:
    return await CategoriesDAO.list(db=db, name=name, limit=limit, offset=offset,)


async def update_category_service(
        db: AsyncSession,
        category_id: int,
        payload: CategoryUpdate,
        ) -> Category:
    category = await CategoriesDAO.get_by_id(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
            )

    update_data = payload.model_dump(exclude_unset=True)

    if "name" in update_data:
        existing_category = await CategoriesDAO.get_by_name(db, update_data["name"])

        if existing_category and existing_category.id != category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists"
                )

        return await CategoriesDAO.update(db, category, update_data)


async def delete_category_service(db: AsyncSession, category_id: int) -> dict:
    category = await CategoriesDAO.get_by_id(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
            )

    await CategoriesDAO.delete(db, category)
    return {"message": "Category deleted successfully"}
