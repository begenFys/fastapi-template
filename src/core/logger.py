"""Configuration Loguru logger."""

import sys
from contextvars import ContextVar

from loguru import logger

LOGGER_REQUEST_ID_CTX = ContextVar("request_id", default="unknown")


def add_request_id(record):  # type: ignore[no-untyped-def]
    """Add request_id in extra."""
    record["extra"]["request_id"] = LOGGER_REQUEST_ID_CTX.get()
    return record


def setup_loguru() -> None:
    """Configure loguru."""
    logger.remove()

    logger.add(
        sink=sys.stderr,
        format="<blue>{time:YYYY-MM-DD HH:mm:ss Z}</blue> | "
        "<level>{level.icon}{level}</level> | "
        "<magenta>{module}:{function}</magenta> - "
        "<white>{message}</white>; <italic>extra:</italic> {extra}",
        colorize=True,
        filter=add_request_id,
    )
