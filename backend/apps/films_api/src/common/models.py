from typing import Generic, TypeVar
from uuid import UUID

import orjson
from pydantic import BaseModel

ModelType = TypeVar("ModelType")


def orjson_dumps(value, *, default):
    return orjson.dumps(value, default=default).decode()


class AppBaseModel(BaseModel, Generic[ModelType]):
    id: UUID

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
