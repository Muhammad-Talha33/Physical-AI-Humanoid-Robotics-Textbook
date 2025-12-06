"""Structured logging with correlation IDs."""
import logging
import sys
import uuid
from contextvars import ContextVar
from typing import Optional
import structlog

# Context variable for correlation ID
correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


def get_correlation_id() -> str:
    """Get or create correlation ID for request tracing."""
    cid = correlation_id.get()
    if cid is None:
        cid = str(uuid.uuid4())
        correlation_id.set(cid)
    return cid


def set_correlation_id(cid: str) -> None:
    """Set correlation ID for request tracing."""
    correlation_id.set(cid)


def add_correlation_id(logger, method_name, event_dict):
    """Add correlation ID to log events."""
    event_dict["correlation_id"] = get_correlation_id()
    return event_dict


# Configure structlog
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        add_correlation_id,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)


def get_logger(name: str):
    """Get a structured logger instance."""
    return structlog.get_logger(name)


# Create default logger
logger = get_logger(__name__)
