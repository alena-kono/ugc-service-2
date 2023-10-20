from src.common.models import AppBaseModel
from src.genres.models import Genre
from src.persons.models import BasePerson


class Film(AppBaseModel):
    imdb_rating: float | None
    description: str | None
    title: str
    actors_names: list[str]
    writers_names: list[str]
    genres: list[Genre]
    actors: list[BasePerson]
    writers: list[BasePerson]
    directors: list[BasePerson]
