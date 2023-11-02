import pydantic
from src.settings.base import BaseAppSettings


class KafkaSettings(BaseAppSettings):
    host: str = pydantic.Field(env="KAFKA_HOST", default="localhost")
    port: int = pydantic.Field(env="KAFKA_PORT", default=9092)
    consumer_group_id: str = pydantic.Field(env="KAFKA_GROUP_ID")
    topic: str = pydantic.Field(env="KAFKA_TOPIC")
    dlq: str = pydantic.Field(env="KAFKA_DLQ")

    @property
    def dsn(self) -> str:
        return f"{self.host}:{self.port}"
