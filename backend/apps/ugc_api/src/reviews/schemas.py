from pydantic import Field
from src.common.schemas import BaseMongoSchema, BaseSchema
from typing_extensions import Self


class ReviewBaseRequestSchema(BaseSchema):
    film_id: str


class ReviewBaseResponseSchema(BaseMongoSchema):
    film_id: str


class ReviewCreateRequestSchema(ReviewBaseRequestSchema):
    text: str
    timestamp: int = Field(..., ge=0)


class ReviewUpdateRequestSchema(ReviewBaseRequestSchema):
    text: str
    timestamp: int = Field(..., ge=0)


class ReviewCreateResponseSchema(ReviewBaseResponseSchema):
    timestamp: int
    user_id: str
    text: str

    @classmethod
    def from_input_schema(
        cls, input_schema: ReviewCreateRequestSchema, user_id: str
    ) -> Self:
        return cls(
            _id=None,
            user_id=user_id,
            film_id=input_schema.film_id,
            timestamp=input_schema.timestamp,
            text=input_schema.text,
        )


class ReviewUpdateResponseSchema(ReviewBaseResponseSchema):
    timestamp: int
    user_id: str
    text: str

    @classmethod
    def from_input_schema(
        cls, input_schema: ReviewUpdateRequestSchema, user_id: str
    ) -> Self:
        return cls(
            _id=None,
            user_id=user_id,
            film_id=input_schema.film_id,
            timestamp=input_schema.timestamp,
            text=input_schema.text,
        )


class ReviewResponseSchema(ReviewBaseResponseSchema):
    timestamp: float
    text: str
    user_id: str
