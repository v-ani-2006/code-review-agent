from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import logger


def get_utc_timestamp() -> str:
    """Return the current UTC timestamp formatted as ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle standard HTTP exceptions like 404 Not Found, 401 Unauthorized, etc."""
    error_code = "HTTP_ERROR"
    if exc.status_code == 404:
        error_code = "NOT_FOUND"
    elif exc.status_code == 403:
        error_code = "FORBIDDEN"
    elif exc.status_code == 401:
        error_code = "UNAUTHORIZED"

    logger.warning(
        "HTTP %d error on %s %s: %s",
        exc.status_code,
        request.method,
        request.url.path,
        exc.detail,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": str(exc.detail),
            "detail": exc.detail,
            "error_code": error_code,
            "timestamp": get_utc_timestamp(),
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle 422 Unprocessable Entity when client input fails schema validation."""
    logger.warning(
        "Validation error on %s %s: %s",
        request.method,
        request.url.path,
        exc.errors(),
    )

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Input validation failed. Please check your request parameters or body.",
            "error_code": "VALIDATION_ERROR",
            "errors": exc.errors(),
            "detail": exc.errors(),
            "timestamp": get_utc_timestamp(),
        },
    )


async def integrity_exception_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """Handle database integrity and unique constraint errors (e.g., duplicate email/username)."""
    error_detail = str(exc.orig).lower() if exc.orig else str(exc).lower()
    logger.warning("Database integrity constraint triggered on %s %s: %s", request.method, request.url.path, error_detail)

    if "email" in error_detail:
        message = "A user account with this email address already exists."
        error_code = "DUPLICATE_EMAIL"
    elif "username" in error_detail:
        message = "A user account with this username already exists."
        error_code = "DUPLICATE_USERNAME"
    elif "foreign key" in error_detail:
        message = "Referenced parent entity does not exist."
        error_code = "FOREIGN_KEY_VIOLATION"
    else:
        message = "Database operation violates integrity constraints."
        error_code = "INTEGRITY_CONSTRAINT_ERROR"

    return JSONResponse(
        status_code=409,
        content={
            "success": False,
            "message": message,
            "detail": message,
            "error_code": error_code,
            "timestamp": get_utc_timestamp(),
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle 500 Internal Server Errors for unexpected exceptions, preventing traceback leaks."""
    logger.exception(
        "Unhandled internal error during %s %s: %s",
        request.method,
        request.url.path,
        str(exc),
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "An internal server error occurred. Please contact the administrator.",
            "detail": "An internal server error occurred. Please contact the administrator.",
            "error_code": "INTERNAL_SERVER_ERROR",
            "timestamp": get_utc_timestamp(),
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all centralized exception handlers with the FastAPI application."""
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
