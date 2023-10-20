from src.common.schemas import AppBaseModel, AppBaseSchema
from src.genres.schemas import Genre
from src.persons.schemas import FilmPerson


class Film(AppBaseSchema):
    title: str
    imdb_rating: float | None

    @classmethod
    def from_model(cls, model: AppBaseModel) -> "Film":
        return cls(**model.dict())


class DetailFilm(Film):
    description: str | None
    genres: list[Genre] | None
    actors: list[FilmPerson]
    writers: list[FilmPerson]
    directors: list[FilmPerson]

    @classmethod
    def from_model(cls, model: AppBaseModel) -> "DetailFilm":
        return cls(**model.dict())
