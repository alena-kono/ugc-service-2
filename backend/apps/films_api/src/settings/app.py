import pydantic
from src.settings.auth import AuthSettings
from src.settings.base import BaseAppSettings
from src.settings.db import ElasticSettings, RedisSettings
from src.settings.jaeger import JaegerSettings
from src.settings.logging import LoggingSettings
from src.settings.service import ServiceSettings


class AppSettings(BaseAppSettings["AppSettings"]):
    is_development: bool = pydantic.Field(env="IS_DEVELOPMENT", default=False)

    logging = LoggingSettings()
    elastic = ElasticSettings()
    redis = RedisSettings()
    service = ServiceSettings()
    auth = AuthSettings()
    jaeger = JaegerSettings()
