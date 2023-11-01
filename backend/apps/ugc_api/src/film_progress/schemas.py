from src.common.schemas import BaseMongoSchema, BaseSchema
from typing_extensions import Self


class FilmProgressBaseRequestSchema(BaseSchema):
    film_id: str


class FilmProgressBaseResponseSchema(BaseMongoSchema):
    film_id: str


class FilmProgressCreateRequestSchema(FilmProgressBaseRequestSchema):
    timestamp: float
    progress_sec: int


class FilmProgressCreateResponseSchema(FilmProgressBaseResponseSchema):
    timestamp: float
    progress_sec: int
    user_id: str

    @classmethod
    def from_input_schema(
        cls, input_schema: FilmProgressCreateRequestSchema, user_id: str
    ) -> Self:
        return cls(
            _id=None,
            user_id=user_id,
            film_id=input_schema.film_id,
            timestamp=input_schema.timestamp,
            progress_sec=input_schema.progress_sec,
        )


class FilmProgressResponseSchema(FilmProgressBaseResponseSchema):
    timestamp: float
    progress_sec: int
    user_id: str
