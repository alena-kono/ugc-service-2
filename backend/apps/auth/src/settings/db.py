import pydantic
from src.settings.base import BaseAppSettings


class PostgresSettings(BaseAppSettings):
    dbname: str = pydantic.Field(env="POSTGRES_DB")
    user: str = pydantic.Field(env="POSTGRES_USER")
    password: str = pydantic.Field(env="POSTGRES_PASSWORD")
    host: str = pydantic.Field(env="POSTGRES_HOST")
    port: int = pydantic.Field(env="POSTGRES_PORT")
    scheme: str = "postgresql+psycopg"

    @property
    def dsn(self) -> str:
        return str(
            pydantic.PostgresDsn.build(
                scheme=self.scheme,
                user=self.user,
                password=self.password,
                host=self.host,
                port=str(self.port),
                path=f"/{self.dbname}",
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
