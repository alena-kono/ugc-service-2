from enum import Enum

from pydantic import Field
from src.common.models import AppBaseModel


class RoleType(str, Enum):
    DIRECTOR: str = "director"
    WRITER: str = "writer"
    ACTOR: str = "actor"


class PersonFilm(AppBaseModel):
    roles: list[RoleType]


class BasePerson(AppBaseModel):
    full_name: str


class Person(BasePerson):
    films: list[PersonFilm] = Field(default_factory=list)
