import pydantic
from src.settings.base import BaseAppSettings


class KafkaSettings(BaseAppSettings):
    host: str = pydantic.Field(env="KAFKA_HOST", default="127.0.0.1")
    port: int = pydantic.Field(env="KAFKA_PORT", default=9092)

    @property
    def dsn(self) -> str:
        return f"{self.host}:{self.port}"
