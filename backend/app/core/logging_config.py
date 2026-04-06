import logging
import json
from datetime import datetime

from app.core.request_id import get_request_id


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        request_id = get_request_id()
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "request_id": request_id,
        }

        skip_fields = {"name",
                       "msg",
                       "args",
                       "levelname",
                       "levelno",
                       "pathname",
                       "filename",
                       "module",
                       "exc_info",
                       "exc_text",
                       "stack_info",
                       "lineno",
                       "funcName",
                       "created",
                       "msecs",
                       "relativeCreated",
                       "thread",
                       "threadName",
                       "processName",
                       "process",
                       }
        for key, value in record.__dict__.items():
            if key not in skip_fields:
                log_record[key] = value

        return json.dumps(log_record)


def setup_logging():
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers = [handler]
