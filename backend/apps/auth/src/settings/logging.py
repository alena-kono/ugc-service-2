import datetime
import logging
import typing as tp
from enum import Enum

import pydantic
import structlog
from src.settings.base import BaseAppSettings


class LoggerLevelType(str, Enum):
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"


class LoggingSettings(BaseAppSettings):
    class Config:
        use_enum_values = True

    level: LoggerLevelType = pydantic.Field(
        env="LOGGING_LEVEL", default=LoggerLevelType.DEBUG
    )
    file_path_json: str = pydantic.Field(
        env="LOGGING_FILE_PATH_JSON", default="../../../logs/apps/auth.log"
    )

    @property
    def config(self) -> dict[str, tp.Any]:
        return {
            "version": 1,
            "disable_existing_loggers": True,
            "formatters": {
                "json_formatter": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": structlog.processors.JSONRenderer(),
                },
                "plain_console": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": structlog.dev.ConsoleRenderer(),
                },
            },
            "handlers": {
                "console": {
                    "level": self.level,
                    "class": "logging.StreamHandler",
                    "formatter": "plain_console",
                },
                "json_file": {
                    "level": self.level,
                    "class": "logging.handlers.TimedRotatingFileHandler",
                    "when": "midnight",
                    "atTime": datetime.time(hour=0),
                    "interval": 1,
                    "backupCount": 2,
                    "filename": self.file_path_json,
                    "formatter": "json_formatter",
                },
            },
            "loggers": {
                "": {
                    "handlers": ["console", "json_file"],
                    "level": self.level,
                }
            },
        }


def configure_logger(enable_async_logger: bool = False) -> None:
    """Configure structlog logger.

    Args:
        enable_async_logger: Enable async logger. Default: False.

    Returns:
        None.

    Note:
        Async logger should be called within async context.
    """
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ExtraAdder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]

    logger_wrapper = structlog.stdlib.BoundLogger
    if enable_async_logger:
        logger_wrapper = structlog.stdlib.AsyncBoundLogger

    structlog.configure(
        processors=shared_processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=logger_wrapper,
        cache_logger_on_first_use=True,
    )

    _clear_log_handlers(["uvicorn.access", "uvicorn.error"])


def _clear_log_handlers(loggers_names: list[str]) -> None:
    """Clear the log handlers for loggers, and enable propagation."""
    for _log in loggers_names:
        logging.getLogger(_log).handlers.clear()
        logging.getLogger(_log).propagate = True
