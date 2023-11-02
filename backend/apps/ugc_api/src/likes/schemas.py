from pydantic import Field
from src.common.schemas import BaseMongoSchema, BaseSchema
from typing_extensions import Self


class LikeBaseRequestSchema(BaseSchema):
    film_id: str


class LikeBaseResponseSchema(BaseMongoSchema):
    film_id: str


class LikeCreateRequestSchema(LikeBaseRequestSchema):
    rank: int = Field(..., ge=1, le=10)
    timestamp: int = Field(..., ge=0)


class LikeUpdateRequestSchema(LikeBaseRequestSchema):
    rank: int = Field(..., ge=1, le=10)
    timestamp: int = Field(..., ge=0)


class LikeCreateResponseSchema(LikeBaseResponseSchema):
    timestamp: int
    user_id: str
    rank: int

    @classmethod
    def from_input_schema(
        cls, input_schema: LikeCreateRequestSchema, user_id: str
    ) -> Self:
        return cls(
            _id=None,
            user_id=user_id,
            film_id=input_schema.film_id,
            timestamp=input_schema.timestamp,
            rank=input_schema.rank,
        )


class LikeUpdateResponseSchema(LikeBaseResponseSchema):
    timestamp: int
    user_id: str
    rank: int

    @classmethod
    def from_input_schema(
        cls, input_schema: LikeUpdateRequestSchema, user_id: str
    ) -> Self:
        return cls(
            _id=None,
            user_id=user_id,
            film_id=input_schema.film_id,
            timestamp=input_schema.timestamp,
            rank=input_schema.rank,
        )


class LikeResponseSchema(LikeBaseResponseSchema):
    timestamp: float
    rank: int
    user_id: str


class TotalLikesResponseSchema(BaseSchema):
    total_likes: int
    film_id: str


class AverageRankResponseSchema(BaseSchema):
    average_rank: float
    film_id: str
