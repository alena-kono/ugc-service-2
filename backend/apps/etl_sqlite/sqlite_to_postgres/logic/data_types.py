from datetime import datetime
from enum import Enum, unique
from typing import Any, Iterable
from uuid import uuid4

from pydantic import BaseModel, Field, validator


class GenericTable(BaseModel):
    def get_columns(self) -> Iterable[str]:
        columns = self.dict().keys()
        return sorted(columns)

    def get_rows(self) -> Iterable[Any]:
        columns = self.get_columns()
        table_data = self.dict()
        return [table_data[column] for column in columns]

    class Config:
        asllow_mutation = False
        use_enum_values = True
        allow_population_by_alias = True


class UUIDMixin(GenericTable):
    id: str = Field(default_factory=str)


class TimeStampedMixin(GenericTable):
    created: datetime = Field(alias="created_at")
    modified: datetime = Field(alias="updated_at")

    @classmethod
    @validator("created", "modified")
    def date_now(cls, date: str, values: dict[str, str], **kwargs) -> datetime:
        return datetime.now()


class Genre(UUIDMixin, TimeStampedMixin):
    name: str
    description: str | None

    @classmethod
    @validator("name")
    def name_max_length(cls, name: str, values: dict[str, str], **kwargs) -> str:
        if len(name) > 255:
            raise ValueError("Name column length should be less or equal 255")
        return name


class FilmWork(UUIDMixin, TimeStampedMixin):
    title: str
    description: str | None
    creation_date: datetime | None
    rating: float | None
    type: str
    file_path: str | None


class Person(UUIDMixin, TimeStampedMixin):
    full_name: str


class PersonFilmWork(UUIDMixin):
    film_work_id: str = Field(default_factory=uuid4)
    person_id: str = Field(default_factory=uuid4)

    role: str
    created: datetime = Field(alias="created_at")

    @classmethod
    @validator("created")
    def date_now(cls, date: str, values: dict[str, str], **kwargs) -> datetime:
        return datetime.now()


class GenreFilmwork(UUIDMixin):
    film_work_id: str = Field(default_factory=uuid4)
    genre_id: str = Field(default_factory=uuid4)

    created: datetime = Field(alias="created_at")

    @classmethod
    @validator("created")
    def date_now(cls, date: str, values: dict[str, str], **kwargs) -> datetime:
        return datetime.now()


@unique
class TableType(Enum):
    GENRE = "genre"
    FILMWORK = "film_work"
    GENREFILMWORK = "genre_film_work"
    PERSONFILMWORK = "person_film_work"
    PERSON = "person"


class TableData(GenericTable):
    table_name: TableType
    data: list[dict[str, Any]]


class PGSettings(BaseModel):
    dbname: str
    user: str
    password: str
    host: str
    port: int

    class Config:
        asllow_mutation = False
