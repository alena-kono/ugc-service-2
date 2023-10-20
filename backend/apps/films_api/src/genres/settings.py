import pydantic
from src.settings.base import BaseAppSettings


class GenreSettings(BaseAppSettings["GenreSettings"]):
    elastic_index: str = pydantic.Field(env="GENRE_ELASTIC_INDEX")
    cache_expire_in_seconds: int = pydantic.Field(
        env="GENRE_CACHE_EXPIRE_IN_SECONDS",
        default=300,
    )
