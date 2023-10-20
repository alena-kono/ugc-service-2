from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Generic, TypeVar, cast
from uuid import UUID

from pydantic import BaseModel, Field

ESDocType = TypeVar("ESDocType", "ESGenreDoc", "ESMovieDoc", "ESPerson")
SQLRowType = TypeVar("SQLRowType", "GenreRow", "MovieRow", "PersonRow")


class BasicSQLRowDataInt(ABC):
    @abstractmethod
    def transform_to_es_doc(self) -> BaseModel:
        ...


class ContainerMixin(BaseModel):
    class Config:
        arbitrary_types_allowed = True


class Roles(Enum):
    ACTOR = "actor"
    DIRECTOR = "director"
    WRITTER = "writer"


class ESPerson(BaseModel):
    person_id: str = Field(alias="id")
    full_name: str


class ESGenre(BaseModel):
    genre_id: str = Field(alias="id")
    name: str


class ESMovieDoc(BaseModel):
    movie_id: str = Field(alias="id")
    imdb_rating: float | None
    title: str
    description: str | None

    actors_names: list[str]
    writers_names: list[str]
    directors_names: list[str]

    directors: list[ESPerson]
    actors: list[ESPerson]
    writers: list[ESPerson]

    genres: list[ESGenre]


class ESGenreDoc(BaseModel):
    genre_id: str = Field(alias="id")
    name: str
    description: str | None


class ESContainer(ContainerMixin, Generic[ESDocType]):
    bulk: list[ESDocType]

    def to_actions(self, index: str) -> list[dict]:
        actions: list[dict] = []
        for doc in self.bulk:
            doc_data = doc.dict(by_alias=True)
            actions.append(
                {
                    "_id": doc_data["id"],
                    "_index": index,
                    **doc_data,
                }
            )

        return actions


class Person(BaseModel):
    person_id: UUID
    person_name: str
    person_role: Roles


class Genre(BaseModel):
    genre_id: UUID
    genre_name: str


class MovieRow(BaseModel, BasicSQLRowDataInt):
    film_id: UUID = Field(alias="id")
    title: str
    description: str | None
    rating: float | None
    film_type: str = Field(alias="type")
    created: datetime
    modified: datetime
    genres: list[Genre]
    persons: list[Person]

    def transform_to_es_doc(self) -> ESMovieDoc:
        def get_persons_by(role: Roles) -> list[ESPerson]:
            return [
                ESPerson(id=str(i.person_id), full_name=i.person_name)
                for i in self.persons
                if i.person_role == role
            ]

        actors = get_persons_by(Roles.ACTOR)
        writers = get_persons_by(Roles.WRITTER)
        directors = get_persons_by(Roles.DIRECTOR)

        actors_names = [i.full_name for i in actors]
        writers_names = [i.full_name for i in writers]
        directors_names = [i.full_name for i in directors]

        genres = [
            ESGenre(id=str(genre.genre_id), name=genre.genre_name)
            for genre in self.genres
        ]

        es_index = ESMovieDoc(
            id=str(self.film_id),
            imdb_rating=self.rating,
            genres=genres,
            title=self.title,
            description=self.description,
            directors=directors,
            directors_names=directors_names,
            actors_names=actors_names,
            writers_names=writers_names,
            actors=actors,
            writers=writers,
        )

        return es_index


class GenreRow(BaseModel, BasicSQLRowDataInt):
    genre_id: str = Field(alias="id")
    name: str
    description: str | None

    def transform_to_es_doc(self) -> BaseModel:
        return ESGenreDoc(**self.dict(by_alias=True))


class PersonRow(BaseModel, BasicSQLRowDataInt):
    person_id: str = Field(alias="id")
    full_name: str

    def transform_to_es_doc(self) -> BaseModel:
        return ESPerson(id=self.person_id, full_name=self.full_name)


class SQLContainer(ContainerMixin, Generic[SQLRowType, ESDocType]):
    batch: list[SQLRowType]

    def transform(self) -> ESContainer:
        es_indexes = [i.transform_to_es_doc() for i in self.batch]
        return ESContainer[ESDocType](bulk=cast(list[ESDocType], es_indexes))
