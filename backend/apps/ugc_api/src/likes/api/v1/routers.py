import logging

from fastapi import APIRouter
from src.common.dependencies import RateLimiterType, UserToken
from src.likes import schemas
from src.likes.dependencies import LikeServiceType

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    path="/likes",
    response_model=schemas.LikeCreateResponseSchema,
    summary="create user's like record",
    description="An endpoint for handling user's like events",
    response_description="like record",
)
async def create_like(
    _: RateLimiterType,
    service: LikeServiceType,
    user: UserToken,
    request_body: schemas.LikeCreateRequestSchema,
) -> schemas.LikeCreateResponseSchema:
    return await service.create_like_record(
        create_request_body=request_body,
        user_id=user.user.id,
    )


@router.get(
    path="/like",
    response_model=schemas.LikeResponseSchema,
    summary="get user's like record",
    description="An endpoint for getting user's like record",
    response_description="like record",
)
async def get_like(
    _: RateLimiterType,
    service: LikeServiceType,
    user: UserToken,
    film_id: str,
) -> schemas.LikeResponseSchema:
    return await service.get_user_like(
        user_id=user.user.id,
        film_id=film_id,
    )


@router.get(
    path="/total-likes",
    response_model=schemas.TotalLikesResponseSchema,
    summary="get total likes",
    description="An endpoint for getting total likes",
    response_description="total likes",
)
async def get_total_likes(
    _: RateLimiterType,
    service: LikeServiceType,
    film_id: str,
) -> schemas.TotalLikesResponseSchema:
    return await service.get_total_likes(film_id=film_id)


@router.get(
    path="/average-rank",
    response_model=schemas.AverageRankResponseSchema,
    summary="get average rank",
    description="An endpoint for getting average rank",
    response_description="average rank",
)
async def get_average_rank(
    _: RateLimiterType,
    service: LikeServiceType,
    film_id: str,
) -> schemas.AverageRankResponseSchema:
    return await service.get_average_rank(film_id=film_id)
