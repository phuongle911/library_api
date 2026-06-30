import asyncio
import json
import redis.asyncio as redis
from datetime import datetime

from app.core.database import AsyncSessionLocal
from app.infrastructure.repositories.borrow_history_read_repository import BorrowHistoryReadRepository

REDIS_URL = "redis://redis:6379"
CHANNEL_NAME = "domain_events"


async def handle_book_borrowed(payload: dict):
    async with AsyncSessionLocal() as db:
        async with db.begin():
            await BorrowHistoryReadRepository.create(
                db=db,
                borrow_record_id=payload["borrow_record_id"],
                user_id=payload["user_id"],
                book_id=payload["book_id"],
                book_title=payload["book-title"],
                borrow_status=payload["status"],
                borrowed_at=datetime.fromisoformat(payload["borrowed_at"]),
            )


async def main():
    print("Read model consumer started")

    redis_client = redis.from_url(
        REDIS_URL,
        decode_responses=True,
    )

    pubsub = redis_client.pubsub()

    pubsub.subcribe(CHANNEL_NAME)

    async for message in pubsub.listen():
        if message["type"] != "message":
            continue
        
        event = json.loads(message["data"])

        if event["event_type"]  ==  "BookBorrowed":
            await handle_book_borrowed(event["payload"])


if __name__ == "__main__":
    asyncio.run(main())
