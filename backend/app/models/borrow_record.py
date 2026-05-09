from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class BorrowRecord(Base):
    __tablename__ = "borrow_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String, nullable=False, default="borrowed")
    borrowed_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    returned_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="borrow_records")
    book = relationship("Book", back_populates="borrow_records")
