import pydantic
from src.settings.base import BaseAppSettings


class FilmSettings(BaseAppSettings["FilmSettings"]):
    elastic_index: str = pydantic.Field(env="FILM_ELASTIC_INDEX")
    cache_expire_in_seconds: int = pydantic.Field(
        env="FILM_CACHE_EXPIRE_IN_SECONDS",
        default=300,
    )
