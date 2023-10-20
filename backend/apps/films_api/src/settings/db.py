from typing import Literal

import pydantic
from src.settings.base import BaseAppSettings


class ElasticSettings(BaseAppSettings):
    host: str = pydantic.Field(env="ELASTIC_HOST")
    port: int = pydantic.Field(env="ELASTIC_PORT")

    max_docs_to_fetch_at_one_time: Literal[10_000] = 10_000

    @property
    def dsn(self) -> str:
        return str(
            pydantic.AnyUrl.build(
                scheme="http",
                host=self.host,
                port=str(self.port),
            )
        )


class RedisSettings(BaseAppSettings):
    host: str = pydantic.Field(env="REDIS_HOST")
    port: int = pydantic.Field(env="REDIS_PORT")

    @property
    def dsn(self) -> str:
        return str(
            pydantic.RedisDsn.build(
                scheme="redis",
                host=self.host,
                port=str(self.port),
            )
        )
