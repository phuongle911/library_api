from datetime import datetime
from sqlalchemy import Column, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class BorrowRecord(Base):
    __tablename__ = "borrow_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    borrowed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    returned_at = Column(DateTime(timezone=True), nullable=True)
    #_table_args_ = (UniqueConstraint("user_id", "book_id", "returned_at", name="uq_active_borrow_per_user_book"),)
