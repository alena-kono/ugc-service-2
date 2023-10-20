from typing import Any

import orjson
from pydantic import BaseModel


def orjson_dumps(value, *, default):
    return orjson.dumps(value, default=default).decode()


class AppBaseSchema(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class BaseEvent(AppBaseSchema):
    film_id: str
    progress_sec: int
    timestamp: float


class FilmProgressEvent(BaseEvent):
    ...


class FilmProgressOutputMsg(AppBaseSchema):
    user_id: str
    film_id: str
    progress_sec: int
    timestamp: float


class JwtUserSchema(AppBaseSchema):
    id: str
    permissions: list[str]


class JwtClaims(AppBaseSchema):
    user: JwtUserSchema
    access_jti: str
    refresh_jti: str
    type: str
    exp: int
    iat: int
