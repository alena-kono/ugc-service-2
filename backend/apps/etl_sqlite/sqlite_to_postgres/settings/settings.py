from pathlib import Path

from pydantic import BaseSettings, Field

BASE_DIR = Path(__name__).resolve().parent


class Settings(BaseSettings):
    dbname: str = Field(env="DB_NAME")
    user: str = Field(env="DB_USER")
    password: str = Field(env="DB_PASSWORD")
    host: str = Field(env="DB_HOST")
    port: int = Field(env="DB_PORT")

    sqlite_file_path: Path = BASE_DIR.joinpath("db.sqlite").absolute()
    chunk_size: int = 50
