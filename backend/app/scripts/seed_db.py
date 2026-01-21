import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.books import Book
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
        # 2) Create books linked to this user (owner_id NOT NULL)
        books = [
            Book(title="Clean Code", description=None, author="Robert C. Martin", owner_id=user.id),
            Book(title="The Pragmatic Programmer", description=None, author="Andrew Hunt", owner_id=user.id),
        ]
        session.add_all(books)
        await session.commit()
        print(f"Seeded user_id={user.id} and {len(books)} books")
if __name__ == "__main__":
    asyncio.run(seed())

