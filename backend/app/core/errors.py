from dataclasses import dataclass


@dataclass
class AppError(Exception):
    code: str
    message: str
    status_code: int = 400


def error_payload(code:str, message: str, request_id: str | None):
    return {"error": {"code": code, "message": message, "request_id": request_id}}


def bad_request(code: str, message: str):
    return AppError(code=code, message=message, status_code=400)