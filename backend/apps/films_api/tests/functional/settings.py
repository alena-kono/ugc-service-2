from functools import lru_cache
from pathlib import Path

import pydantic

ENV_DIR = Path(__file__).resolve().parent.parent.parent.joinpath(".env")


class BaseSettings(pydantic.BaseSettings):
    class Config:
        env_file = ENV_DIR
        env_file_encoding = "utf-8"


class FilmIndexSettings(BaseSettings):
    index: str = pydantic.Field(env="FILM_ELASTIC_INDEX", default="movies")
    field_id_name: str = pydantic.Field(env="FILM_ELASTIC_FIELD_ID", default="id")


class GenreIndexSettings(BaseSettings):
    index: str = pydantic.Field(env="GENRE_ELASTIC_INDEX", default="genres")
    field_id_name: str = pydantic.Field(env="GENRE_ELASTIC_FIELD_ID", default="id")


class PersonIndexSettings(BaseSettings):
    index: str = pydantic.Field(env="PERSON_ELASTIC_INDEX", default="persons")
    field_id_name: str = pydantic.Field(env="PERSON_ELASTIC_FIELD_ID", default="id")


class ElasticSettings(BaseSettings):
    host: str = pydantic.Field(env="ELASTIC_HOST")
    port: int = pydantic.Field(env="ELASTIC_PORT")

    film_index = FilmIndexSettings()
    genre_index = GenreIndexSettings()
    person_index = PersonIndexSettings()

    @property
    def dsn(self) -> str:
        return str(
            pydantic.AnyUrl.build(
                scheme="http",
                host=self.host,
                port=str(self.port),
            )
        )


class RedisSettings(BaseSettings):
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


class BackendSettings(BaseSettings):
    host: str = pydantic.Field(env="TEST_HOST")
    port: str = pydantic.Field(env="TEST_PORT")

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"


class AuthSettings(BaseSettings):
    jwt_encoding_algorithm: str = pydantic.Field(
        env="AUTH_JWT_ENCODING_ALGORITHM",
        default="HS256",
    )
    jwt_secret_key: str = pydantic.Field(env="AUTH_JWT_SECRET_KEY")


class Settings(BaseSettings):
    redis = RedisSettings()
    backend = BackendSettings()
    elastic = ElasticSettings()
    auth = AuthSettings()

    @classmethod
    @lru_cache(maxsize=1)
    def get(cls) -> "Settings":
        return cls()
