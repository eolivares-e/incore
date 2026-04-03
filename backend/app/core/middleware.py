"""Custom middleware for the FastAPI application.

Includes:
- Request/Response logging with request IDs
- Request duration tracking
- Structured logging for debugging and monitoring
"""

import time
import uuid
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = structlog.get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all incoming requests and outgoing responses.

    Features:
    - Generates unique request_id for each request
    - Logs request method, path, client IP
    - Logs response status code and duration
    - Adds request_id to response headers for tracing
    - Excludes health check endpoints from logging (optional)
    """

    def __init__(
        self,
        app: ASGIApp,
        exclude_paths: list[str] | None = None,
    ):
        """Initialize middleware.

        Args:
            app: ASGI application
            exclude_paths: List of paths to exclude from logging (e.g., ["/health"])
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or []

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/endpoint in chain

        Returns:
            HTTP response with added request_id header
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Add request_id to contextvars for all logs in this request
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        # Skip logging for excluded paths
        if request.url.path in self.exclude_paths:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response

        # Get client IP (handle proxies)
        client_ip = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()

        # Log request
        start_time = time.time()
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            query_params=str(request.query_params) if request.query_params else None,
            client_ip=client_ip,
            user_agent=request.headers.get("user-agent"),
        )

        # Process request
        try:
            response = await call_next(request)
        except Exception as exc:
            # Log exception
            duration = time.time() - start_time
            logger.error(
                "request_failed",
                method=request.method,
                path=request.url.path,
                duration_ms=round(duration * 1000, 2),
                error=str(exc),
                error_type=type(exc).__name__,
            )
            raise

        # Calculate duration
        duration = time.time() - start_time

        # Log response
        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration * 1000, 2),
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response
