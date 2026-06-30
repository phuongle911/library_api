from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String

from app.core.database import Base


class BorrowSaga(Base):
    __tablename__ = "borrow_sagas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    book_id = Column(Integer, nullable=False, index=True)
    status = Column(String, nullable=False, default="STARTED")
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
