"""Centralized logging configuration for the application.

Supports two formats:
- JSON: Structured logging for production (machine-readable)
- READABLE: Human-friendly colored logging for development

Usage:
    from app.core.logging import get_logger
    logger = get_logger(__name__)
    logger.info("User logged in", extra={"user_id": user.id})
"""

import logging
import sys
from datetime import datetime
from typing import Any

import structlog
from structlog.types import EventDict, Processor


def add_timestamp(
    logger: logging.Logger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Add ISO 8601 timestamp to log entries."""
    event_dict["timestamp"] = datetime.utcnow().isoformat()
    return event_dict


def add_log_level(
    logger: logging.Logger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Add log level to event dict."""
    event_dict["level"] = method_name.upper()
    return event_dict


def add_logger_name(
    logger: logging.Logger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Add logger name to event dict."""
    if hasattr(logger, "name"):
        event_dict["logger"] = logger.name
    return event_dict


def configure_logging(log_format: str = "json", log_level: str = "INFO") -> None:
    """Configure structlog for the application.

    Args:
        log_format: Either "json" or "readable"
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Set logging level
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # Common processors for both formats
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        add_timestamp,
        add_log_level,
        add_logger_name,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if log_format.lower() == "json":
        # JSON format for production
        processors = shared_processors + [structlog.processors.JSONRenderer()]
    else:
        # Human-readable format for development
        processors = shared_processors + [structlog.dev.ConsoleRenderer(colors=True)]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a logger instance with the given name.

    Args:
        name: Logger name (typically __name__ of the module)

    Returns:
        Configured structlog BoundLogger instance

    Example:
        logger = get_logger(__name__)
        logger.info("user_created", user_id=user.id, email=user.email)
    """
    return structlog.get_logger(name)


# Convenience function for logging function entry/exit (useful for debugging)
def log_function_call(
    logger: structlog.BoundLogger, func_name: str, **kwargs: Any
) -> None:
    """Log function call with parameters.

    Args:
        logger: Logger instance
        func_name: Function name
        **kwargs: Function parameters to log
    """
    logger.debug("function_called", function=func_name, **kwargs)
