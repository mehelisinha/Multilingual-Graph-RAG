"""Custom HTTP exception classes and global handlers."""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.core.logging import get_logger

logger = get_logger(__name__)


class AppHTTPException(HTTPException):
    """Base application HTTP exception."""

    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(status_code=status_code, detail=detail)


class AuthenticationError(AppHTTPException):
    def __init__(self, detail: str = "Could not validate credentials") -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class AuthorizationError(AppHTTPException):
    def __init__(self, detail: str = "Insufficient permissions") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class NotFoundError(AppHTTPException):
    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class PipelineUnavailableError(AppHTTPException):
    def __init__(self, detail: str = "Retrieval pipeline is unavailable") -> None:
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)


async def _unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Log unhandled errors with request context and return a clean 500.

    The request_id bound by RequestIDMiddleware is included automatically via
    structlog contextvars, so log lines correlate with the X-Request-ID header.
    """
    logger.exception(
        "unhandled_exception",
        method=request.method,
        path=request.url.path,
        error=str(exc),
    )
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(Exception, _unhandled_exception_handler)
