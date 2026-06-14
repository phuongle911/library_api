from app.infrastructure.messaging.redis_publisher import RedisEventPublisher

publisher = RedisEventPublisher()


async def publish_event(event_type: str, payload: dict):
    event = {
        "event_type": event_type,
        "payload": payload,
    }

    await publisher.publish("library_events", event)
