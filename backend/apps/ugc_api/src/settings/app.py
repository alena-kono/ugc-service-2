from functools import lru_cache

from src.settings.auth import AuthSettings
from src.settings.base import BaseAppSettings
from src.settings.jaeger import JaegerSettings
from src.settings.logging import LoggingSettings
from src.settings.rate_limiter import RateLimiterSettings
from src.settings.redis import RedisSettings
from src.settings.service import ServiceSettings
from src.settings.kafka import KafkaSettings


class AppSettings(BaseAppSettings):
    logging = LoggingSettings()
    redis = RedisSettings()
    service = ServiceSettings()
    auth = AuthSettings()
    rate_limiter = RateLimiterSettings()
    jaeger = JaegerSettings()
    kafka = KafkaSettings()


@lru_cache(maxsize=1)
def get_app_settings() -> AppSettings:
    return AppSettings()
