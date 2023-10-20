import pydantic
from src.settings.base import BaseAppSettings


class KafkaSettings(BaseAppSettings):
    host: str = pydantic.Field(env="KAFKA_HOST")
    port: int = pydantic.Field(env="KAFKA_PORT")

    @property
    def dsn(self) -> str:
        return f"{self.host}:{self.port}"
