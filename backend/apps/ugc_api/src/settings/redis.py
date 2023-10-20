import pydantic
from src.settings.base import BaseAppSettings


class RedisSettings(BaseAppSettings):
    host: str = pydantic.Field(env="REDIS_HOST")
    port: int = pydantic.Field(env="REDIS_PORT")

    list_name: str = pydantic.Field(env="REDIS_LIST_NAME", default="events")

    @property
    def dsn(self) -> str:
        return str(
            pydantic.RedisDsn.build(
                scheme="redis",
                host=self.host,
                port=str(self.port),
            )
        )
