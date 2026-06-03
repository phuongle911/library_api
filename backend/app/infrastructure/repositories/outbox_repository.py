from datetime import datetime, timezone

from sqlalchemy import select

from app.models.outbox_event import OutboxEvent


class OutboxRepository:

    @staticmethod
    async def create(db, event_type: str, payload: dict):
        event = OutboxEvent(
            event_type=event_type,
            payload=payload,
        )
        db.add(event)
        await db.flush()
        return event

    @staticmethod
    async def get_unprocessed_events(db, limit: int = 10):
        result = await db.execute(
            select(OutboxEvent)
            .where(OutboxEvent.processed_at.is_(None))
            .order_by(OutboxEvent.created_at.asc())
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def mark_processed(db, event: OutboxEvent):
        event.processed_at = datetime.now(timezone.utc)
        await db.flush()
        return event
