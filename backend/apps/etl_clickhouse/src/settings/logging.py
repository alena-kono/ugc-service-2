import logging
import time
from enum import StrEnum, unique
from typing import Any

import pydantic
from src.settings.base import BaseAppSettings


@unique
class LoggerLevelType(StrEnum):
    CRITICAL: str = "CRITICAL"
    ERROR: str = "ERROR"
    WARNING: str = "WARNING"
    INFO: str = "INFO"
    DEBUG: str = "DEBUG"


logging.Formatter.converter = time.gmtime


class LoggingSettings(BaseAppSettings):
    class Config:
        use_enum_values: bool = True

    level: LoggerLevelType = pydantic.Field(
        env="LOGGING_LEVEL", default=LoggerLevelType.INFO
    )

    @property
    def config(self) -> dict[str, Any]:
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "level": "DEBUG",
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                },
            },
            "loggers": {"": {"handlers": ["console"], "level": self.level}},
        }
