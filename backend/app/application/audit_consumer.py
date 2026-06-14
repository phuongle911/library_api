import asyncio
import json
import os
from redis.asyncio import Redis


async def run_audit_consumer():
    redis = Redis.from_url(
        os.getenv("REDIS_URL",
                  "redis://localhost:6379"),
                  decode_responses=True,
    )

    last_id = "0-0"

    while True:
        events = await redis.xread(
            {"library_events":last_id},
            block=5000,
            count=10,
        )

        for stream_name, messages in events:
            for message_id, data in messages:
                event = json.loads(data["data"])

                print("AUDIT EVENT RECEIVED:", event)

                last_id = message_id

                await asyncio.sleep(1)

if __name__ == "__main__":

    asyncio.run(run_audit_consumer())
