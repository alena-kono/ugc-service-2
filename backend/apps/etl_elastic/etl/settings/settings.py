from pathlib import Path

from pydantic import BaseSettings, Field

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR.joinpath(".env").absolute()
ES_SCHEMAS_PATH = BASE_DIR.joinpath("configs/es_schemas")


class CommonSettings(BaseSettings):
    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = "utf-8"


class SystemSettings(CommonSettings):
    synhronization_time_sec: int = 10

    original_wait_for_sevice_time_sec: float = 0.1
    factor: int = 2
    max_value: float = 10


class RedisSettings(CommonSettings):
    host: str = Field(env="REDIS_HOST")
    port: int = Field(env="REDIS_PORT")

    prefix: str = Field(env="REDIS_PREFIX")


class PGSettings(CommonSettings):
    dbname: str = Field(env="DB_NAME")
    user: str = Field(env="DB_USER")
    password: str = Field(env="DB_PASSWORD")
    host: str = Field(env="DB_HOST")
    port: int = Field(env="DB_PORT")


class ESSettings(CommonSettings):
    index: str = Field(env="ES_INDEX")
    host: str = Field(env="ES_HOST")
    port: int = Field(env="ES_PORT")
