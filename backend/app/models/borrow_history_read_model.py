from sqlalchemy import Column, DateTime, Integer, String
from datetime import datetime, timezone

from app.core.database import Base


class BorrowHistoryReadModel(Base):
    __tablename__ = "borrow_history_read_models"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    borrow_record_id = Column(Integer, nullable=False, index=True)

    user_id = Column(Integer, nullable=False, index=True)
    book_id = Column(Integer, nullable=False, index=True)

    book_title = Column(String, nullable=False)
    borrow_status = Column(String, nullable=False)

    borrowed_at = Column(DateTime(timezone=True), nullable=False)
    returned_at = Column(DateTime(timezone=True), nullable=True)

    create_at = Column(DateTime(timezone=True),
                       default=lambda: datetime.now(timezone.utc),
                       nullable=False,
                       )
    updated_at = Column(DateTime(timezone=True),
                        default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc),
                        nullable=False,
                        )


