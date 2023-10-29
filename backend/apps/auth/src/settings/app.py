from functools import lru_cache

import pydantic
from src.settings.auth import AuthSettings
from src.settings.base import BaseAppSettings
from src.settings.db import PostgresSettings, RedisSettings
from src.settings.jaeger import JaegerSettings
from src.settings.logging import LoggingSettings
from src.settings.rate_limiter import RateLimiterSettings
from src.settings.sentry import SentrySettings
from src.settings.service import ServiceSettings
from src.settings.social import SocialSettings


class AppSettings(BaseAppSettings):
    is_development: bool = pydantic.Field(env="IS_DEVELOPMENT", default=False)

    logging = LoggingSettings()
    postgres = PostgresSettings()
    redis = RedisSettings()
    service = ServiceSettings()
    auth = AuthSettings()
    social = SocialSettings()
    rate_limiter = RateLimiterSettings()
    jaeger = JaegerSettings()
    sentry = SentrySettings()


@lru_cache(maxsize=1)
def get_app_settings() -> AppSettings:
    return AppSettings()
