from functools import lru_cache
from pathlib import Path
from typing import Generic, Type, TypeVar

import pydantic

SettingsType = TypeVar("SettingsType")

ENV_DIR = Path(__file__).resolve().parent.parent.parent.joinpath(".env")


class BaseAppSettings(pydantic.BaseSettings, Generic[SettingsType]):
    class Config:
        env_file = ENV_DIR
        env_file_encoding = "utf-8"

    @classmethod
    @lru_cache(maxsize=1)
    def get(cls: Type[SettingsType]) -> SettingsType:
        return cls()
