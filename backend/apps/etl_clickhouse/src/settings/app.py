from functools import lru_cache

import pydantic
from src.settings.base import BaseAppSettings
from src.settings.clickhouse import ClickhouseSettings
from src.settings.etl import ETLSettings
from src.settings.kafka import KafkaSettings
from src.settings.logging import LoggingSettings


class AppSettings(BaseAppSettings):
    pidfile: str = pydantic.Field(env="PIDFILE", default="")

    kafka: KafkaSettings = KafkaSettings()
    etl: ETLSettings = ETLSettings()
    logging: LoggingSettings = LoggingSettings()
    clickhouse: ClickhouseSettings = ClickhouseSettings()


@lru_cache(maxsize=1)
def get_app_settings() -> AppSettings:
    return AppSettings()
