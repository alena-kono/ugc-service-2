from pydantic import Field
from src.common.schemas import AppBaseModel, AppBaseSchema
from src.persons.models import RoleType


class FilmPerson(AppBaseSchema):
    full_name: str


class FilmPersonRole(AppBaseSchema):
    roles: list[RoleType]


class DetailPerson(FilmPerson):
    films: list[FilmPersonRole] = Field(default_factory=list)

    @classmethod
    def from_model(cls, model: AppBaseModel) -> "DetailPerson":
        return cls(**model.dict())
