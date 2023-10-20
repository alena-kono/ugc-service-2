from typing import Type

from src.common.repository import AbstractRepository, ESRepository
from src.common.utils import ESHandler
from src.films.models import Film
from src.films.settings import FilmSettings

film_settings = FilmSettings.get()


class FilmRepository(AbstractRepository[Film]):
    pass


class ESFilmRepository(ESRepository[Film], FilmRepository):
    schema: Type = Film

    def __init__(self, es_handler: ESHandler) -> None:
        super().__init__(es_handler, film_settings.elastic_index)
