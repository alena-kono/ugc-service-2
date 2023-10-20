from pathlib import Path

import pydantic

ENV_DIR = Path(__file__).resolve().parent.parent.parent.joinpath(".env")


class BaseAppSettings(pydantic.BaseSettings):
    class Config:
        env_file = ENV_DIR
        env_file_encoding = "utf-8"
