from src.utils.base_schema import BaseSchema
from src.ugc.input_schemas import (
    InputBaseSchema,
    FilmProgressEvent,
    LikeEvent,
    CommentEvent,
)
from typing import Self, TypeVar, Generic
from pydantic import Field, validator
from pymongo.collection import ObjectId

InputSchemaType = TypeVar("InputSchemaType", bound=InputBaseSchema)


class OutputBaseSchema(BaseSchema, Generic[InputSchemaType]):
    id: str | None = Field(alias="_id")
    user_id: str
    film_id: str
    timestamp: float

    @validator("id", pre=True, always=True)
    @classmethod
    def convert_to_str(cls, _id: ObjectId) -> str:
        return str(_id)

    @classmethod
    def from_input_schema(cls, input_schema: InputSchemaType, user_id: str) -> Self:
        raise NotImplementedError("Method must be implemented in child class.")


class FilmProgressSchema(OutputBaseSchema[FilmProgressEvent]):
    progress_sec: int

    @classmethod
    def from_input_schema(cls, input_schema: FilmProgressEvent, user_id: str) -> Self:
        return cls(
            user_id=user_id,
            film_id=input_schema.film_id,
            timestamp=input_schema.timestamp,
            progress_sec=input_schema.progress_sec,
        )


class LikeSchema(OutputBaseSchema[LikeEvent]):
    @classmethod
    def from_input_schema(cls, input_schema: LikeEvent, user_id: str) -> Self:
        return cls(
            user_id=user_id,
            film_id=input_schema.film_id,
            timestamp=input_schema.timestamp,
        )


class CommentSchema(OutputBaseSchema[CommentEvent]):
    comment: str

    @classmethod
    def from_input_schema(cls, input_schema: CommentEvent, user_id: str) -> Self:
        return cls(
            user_id=user_id,
            film_id=input_schema.film_id,
            timestamp=input_schema.timestamp,
            comment=input_schema.comment,
        )
