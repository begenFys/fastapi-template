"""Log severity."""

from enum import StrEnum


class LogSeverity(StrEnum):
    """Log severity."""
    info = "INFO"
    warning = "WARNING"
    error = "ERROR"
    debug = "DEBUG"
    critical = "CRITICAL"
