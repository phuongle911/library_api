from datetime import datetime
from sqlalchemy import ForeignKey, Integer, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class BorrowRecord(Base):
    __tablename__ = "borrow_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="borrowed")
    borrowed_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
        )

    user = relationship("User", back_populates="borrow_records")
    book = relationship("Book", back_populates="borrow_records")
