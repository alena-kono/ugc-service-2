import pydantic
from src.settings.base import BaseAppSettings


class ETLSettings(BaseAppSettings):
    buffer_size: int = pydantic.Field(env="ETL_MAX_BUFFER_BYTES", default=10000)
    linger_ms: int = pydantic.Field(env="ETL_LINGER_MS", default=100)
