import logging
from dataclasses import asdict, is_dataclass

logger = logging.getLogger(__name__)


async def dispatch_domain_event(event):
    event_name = event.__class__.__name__

    event_data = asdict(event) if is_dataclass(event) else event.__dict__

    logger.info(
        "DOMAIN_EVENT_DISPATCHED",
        extra={
            "event_name": event_name,
            "event_data": event_data,
        },
    )