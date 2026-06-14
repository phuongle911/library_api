import asyncio
from app.application.event_publisher import publish_event
from app.core.database import AsyncSessionLocal
from app.infrastructure.repositories.outbox_repository import OutboxRepository


async def process_outbox_events():
    async with AsyncSessionLocal() as db:
        async with db.begin():
            events = await OutboxRepository.get_unprocessed(db)

            for event in events:
                await publish_event(
                    event_type=event.event_type,
                    payload=event.payload,
                )

                await OutboxRepository.mark_processed(db, event)


async def run_outbox_consumer():
    while True:
        await process_outbox_events()
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(run_outbox_consumer())
