from typing import Type

from src.common.repository import AbstractRepository, ESRepository
from src.common.utils import ESHandler
from src.genres.models import Genre
from src.genres.settings import GenreSettings

genre_settings = GenreSettings.get()


class GenreRepository(AbstractRepository[Genre]):
    pass


class ESGenreRepository(ESRepository[Genre], GenreRepository):
    schema: Type = Genre

    def __init__(self, es_handler: ESHandler) -> None:
        super().__init__(es_handler, genre_settings.elastic_index)
