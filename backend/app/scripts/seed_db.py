import asyncio
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.books import Book
from app.models.categories import Category
from app.models.borrow_record import BorrowRecord


async def seed():
    async with AsyncSessionLocal() as session:
        # 1) Create/find a user
        email = "test1@example.com"
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            user = User(
                name="Test User",
                email=email,
                hashed_password="fakehash",
                role="user",
                is_active=True,
            )
            session.add(user)
            await session.flush()
        # 2) Create categories
        categories_data = [
            {"name": "Programming", "description": "Coding books"},
            {"name": "Fiction", "description": "Story books"},
            ]
        categories = []
        for data in categories_data:
            result = await session.execute(
                select(Category).where(Category.name == data["name"])
            )
            category = result.scalar_one_or_none()
            if not category:
                category = Category(**data)
                session.add(category)
                await session.flush()
            categories.append(category)
        # 3) Create books linked to this user (owner_id NOT NULL)
        books = []
        for i, category in enumerate(categories):
            book = Book(
                title=f"Book {i+1}",
                author="Author",
                description="Sample book",
                owner_id=user.id,
                category_id=category.id,
            )
            session.add(book)
            books.append(book)

            await session.flush()

            for book in books:
                borrow = BorrowRecord(
                    user_id=user.id,
                    book_id=book.id,
                    status="borrowed",  # important field
                )
                session.add_all(books)
                await session.commit()
                print(f"Seeded user_id={user.id} and {len(books)} books")
if __name__ == "__main__":
    asyncio.run(seed())
