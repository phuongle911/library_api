from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.core.database import Base


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, nullable=False, index=True)
    book_id = Column(Integer, nullable=False, index=True)

    status = Column(String, nullable=False, default="pending") # pending, fulfilled, cancelled, expired

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False,)

    fulfilled_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)