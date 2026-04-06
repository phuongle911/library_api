import json
import logging
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        try:
            payload = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "msg": record.getMessage(),
            }

            # include any extras safely
            for k, v in record.__dict__.items():
                if k.startswith("_"):
                    continue
                # keep it small: only simple types, else stringify
                if k not in payload and k not in (
                    "args",
                    "msg",
                    "exc_info",
                    "exc_text",
                    "stack_info"
                      ):
                    payload[k] = v

            if record.exc_info:
                payload["exc_info"] = self.formatException(record.exc_info)

            return json.dumps(payload, ensure_ascii=False, default=str)

        except Exception as e:
            # hard fallback: MUST return a string
            return json.dumps(
                {
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "level": record.levelname,
                    "logger": record.name,
                    "msg": str(record.msg),
                    "format_error": str(e),
                },
                ensure_ascii=False,
            )


def setup_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    handler.setLevel(level.upper())

    # force=True is important to replace uvicorn/sqlalchemy default handlers
    logging.basicConfig(level=level.upper(), handlers=[handler], force=True)
