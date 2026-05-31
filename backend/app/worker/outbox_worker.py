from app.core.database import AsyncSession, AsyncSessionLocal

from app.infrastructure.repositories.outbox_repository import OutboxRepository
from app.domain.events.dispatcher import dispatch_domain_event


async def process_outbox_events():
    async with AsyncSessionLocal() as db:
        events = await OutboxRepository.get_unprocessed_events(db=db, limit=100,)

        for event in events:
            try:
                await dispatch_domain_event(event)
                await OutboxRepository.mark_processed(db=db, event=event,)

                await db.commit()

            except Exception:
                await db.rollback()
