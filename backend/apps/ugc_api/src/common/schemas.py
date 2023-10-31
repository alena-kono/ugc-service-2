import orjson
from pydantic import BaseModel, Field, validator
from pymongo.collection import ObjectId


def orjson_dumps(value, *, default):
    return orjson.dumps(value, default=default).decode()


class BaseSchema(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class BaseMongoSchema(BaseSchema):
    id: str | None = Field(alias="_id")

    @validator("id", pre=True, always=True)
    @classmethod
    def convert_to_str(cls, _id: ObjectId) -> str | None:
        if _id:
            return str(_id)
        return None
