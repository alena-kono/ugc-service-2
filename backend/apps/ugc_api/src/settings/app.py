from functools import lru_cache

from src.settings.auth import AuthSettings
from src.settings.base import BaseAppSettings
from src.settings.jaeger import JaegerSettings
from src.settings.kafka import KafkaSettings
from src.settings.logging import LoggingSettings
from src.settings.mongo import MongoSettings
from src.settings.rate_limiter import RateLimiterSettings
from src.settings.redis import RedisSettings
from src.settings.sentry import SentrySettings
from src.settings.service import ServiceSettings


class AppSettings(BaseAppSettings):
    logging = LoggingSettings()  # type: ignore
    redis = RedisSettings()  # type: ignore
    service = ServiceSettings()  # type: ignore
    auth = AuthSettings()  # type: ignore
    rate_limiter = RateLimiterSettings()  # type: ignore
    jaeger = JaegerSettings()  # type: ignore
    kafka = KafkaSettings()  # type: ignore
    mongo = MongoSettings()  # type: ignore
    sentry = SentrySettings()  # type: ignore


@lru_cache(maxsize=1)
def get_app_settings() -> AppSettings:
    return AppSettings()
