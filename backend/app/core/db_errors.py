from sqlalchemy.exc import IntegrityError, NoResultFound
from app.core.errors import AppError

def map_db_error(exc: Exception) -> AppError:
    if isinstance(exc, NoResultFound):
        return AppError(
            code="NOT_FOUND",
            message="Resource not found",
            status_code=404,
        )
    
    if isinstance(exc, IntegrityError):
        return AppError(
            code="DB_CONSTRAINT_ERROR",
            message="Database constraint violated",
            status_code=409
        )
    
    return AppError(
        code="DB_ERROR",
        message="Database operation failed",
        status_code=500,
    )