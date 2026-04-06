from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.categories import CategoryCreate, CategoryResponse, CategoryUpdate
from app.services.categories_service import (
    create_category_service,
    get_category_by_id_service,
    list_categories_service,
    update_category_service,
    delete_category_service,
)

category_router = APIRouter(prefix="/categories", tags=["Categories"])


@category_router.post(
        "", response_model=CategoryResponse,
        status_code=status.HTTP_201_CREATED,
        )
async def create_category(payload: CategoryCreate, db: AsyncSession = Depends(get_db),):
    return await create_category_service(db, payload)


@category_router.get("", response_model=list[CategoryResponse])
async def list_categories(
    name: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    return await list_categories_service(db=db, name=name, limit=limit, offset=offset,)


@category_router.get(
        "/{category_id}",
        response_model=CategoryResponse,
        status_code=status.HTTP_200_OK,
        )
async def get_category_by_id(category_id: int, db: AsyncSession = Depends(get_db),):
    return await get_category_by_id_service(db, category_id)


@category_router.patch(
        "/{category_id}",
        response_model=CategoryResponse,
        status_code=status.HTTP_200_OK,
        )
async def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
      ):
    return await update_category_service(db, category_id, payload)


@category_router.delete("/{category_id}", status_code=status.HTTP_200_OK,)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db),):
    return await delete_category_service(db, category_id)
