import pydantic
from src.settings.base import BaseAppSettings


class SentrySettings(BaseAppSettings):
    enabled: bool = pydantic.Field(env="SENTRY_ENABLED", default=True)
    dsn: str | None = pydantic.Field(env="SENTRY_DSN", default=None)
