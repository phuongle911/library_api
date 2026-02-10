import json
import logging
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str: 
        payload = {
              "ts": datetime.now(timezone.utc).isoformat(),
              "level": record.levelname,
              "logger": record.getMessage(),
              }
        # Attach "extra" fields if present
        for key in (
            "request_id",
            "method",
            "path",
            "status_code",
            "latency_ms",
            "user_id",
            "ip",
        ):
          if hasattr(record, key):
               payload[key] = getattr(record, key)

        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

            return json.dumps(payload, ensure_ascii=False)


def setup_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)

    handler.setFormatter(JsonFormatter())
    handler.setLevel(level.upper())

    logging.basicConfig(
        level=level.upper(),
        handlers=[handler],
        force=True,
    )
        