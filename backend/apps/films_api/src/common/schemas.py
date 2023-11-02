from uuid import UUID

import orjson
from pydantic import BaseModel, Field, validator
from src.common.models import AppBaseModel, orjson_dumps
from typing_extensions import Self


class BaseSchema(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class AppBaseSchema(BaseSchema):
    uuid: str = Field(alias="id")

    @validator("uuid", pre=True)
    @classmethod
    def validate_uuid(cls, value: UUID) -> str:
        return str(value)

    @classmethod
    def from_model(cls, model: AppBaseModel) -> Self:
        return cls(**model.dict())


class JwtUserSchema(BaseSchema):
    id: str
    permissions: list[str]


class JwtClaims(BaseSchema):
    user: JwtUserSchema
    access_jti: str
    refresh_jti: str
    type: str
    exp: int
    iat: int
