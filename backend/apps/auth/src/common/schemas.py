from datetime import datetime
from uuid import UUID

import orjson
from pydantic import BaseModel


def orjson_dumps(value, *, default):
    return orjson.dumps(value, default=default).decode()


class AppBaseSchema(BaseModel):
    class Config:
        orm_mode = True
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class UUIDSchemaMixin(AppBaseSchema):
    id: UUID


class TimestampSchemaMixin(AppBaseSchema):
    created_at: datetime
    modified_at: datetime
