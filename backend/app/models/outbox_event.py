from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, JSON

from app.core.database import Base


class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    id = Column(Integer, primary_key=True)

    event_type = Column(String, nullable=False)

    payload = Column(JSON, nullable=False)

    processed_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
