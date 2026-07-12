import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings


# write database (primary)
write_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.SQL_ECHO,
    future=True,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
)

# read database (replica)
# currently same DB
read_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.SQL_ECHO,
    future=True,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
)

WriteSessionLocal = sessionmaker(
    bind=write_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

ReadSessionLocal = sessionmaker(
    bind=read_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

# write DB dependency
async def get_db():
    async with WriteSessionLocal() as session:
        yield session

# read DB dependency
async def get_read_db():
    async with ReadSessionLocal() as session:
        yield session

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.SQL_ECHO,
    future=True,

    # connection pool settings
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()
