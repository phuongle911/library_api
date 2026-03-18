from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.categories import Category


class CategoriesDAO:
    @staticmethod
    async def create(db: AsyncSession, payload: dict) -> Category:
        category = Category(**payload)
        db.add(category)
        await db.commit()
        await db.refresh(category)
        return category

    @staticmethod
    async def get_by_id(db: AsyncSession, category_id: int) -> Category | None:
        result = await db.execute(select(Category).where(Category.id == category_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Category | None:
        result = await db.execute(select(Category).where(Category.name == name))
        return result.scalar_one_or_none()

    @staticmethod
    async def list(
        db: AsyncSession,
        name: str | None = None,
        limit: int = 50,
        offset: int = 0,
        ) -> list[
            Category
            ]:
        query = select(Category)

        if name:
            query = query.where(Category.name.ilike(f"%{name}%"))

        query = query.order_by(Category.id.desc()).limit(limit).offset(offset)

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update(db: AsyncSession, category: Category, payload: dict,) -> Category:
        for key, value in payload.items():
            setattr(category, key, value)

            await db.commit()
            await db.refresh(category)
            return category

    @staticmethod
    async def delete(db: AsyncSession, category: Category) -> None:
        await db.delete(category)
        await db.commit()
