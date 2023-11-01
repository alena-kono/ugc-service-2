import logging

from fastapi import APIRouter, Depends
from fastapi_pagination import Page, Params

from src.common.dependencies import RateLimiterType, UserToken
from src.reviews import schemas
from src.reviews.dependencies import ReviewServiceType

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    path="/reviews",
    response_model=schemas.ReviewCreateResponseSchema,
    summary="create user's review record",
    description="An endpoint for handling user's review events",
    response_description="review record",
)
async def create_review(
    _: RateLimiterType,
    service: ReviewServiceType,
    user: UserToken,
    request_body: schemas.ReviewCreateRequestSchema,
) -> schemas.ReviewCreateResponseSchema:
    return await service.create_review_record(
        create_request_body=request_body,
        user_id=user.user.id,
    )


@router.put(
    path="/reviews/{review_id:str}",
    response_model=schemas.ReviewUpdateResponseSchema,
    summary="create user's review record",
    description="An endpoint for handling user's review events",
    response_description="review record",
)
async def update_review(
    review_id: str,
    _: RateLimiterType,
    service: ReviewServiceType,
    user: UserToken,
    request_body: schemas.ReviewUpdateRequestSchema,
) -> schemas.ReviewUpdateResponseSchema:
    return await service.update_review_record(
        review_id=review_id,
        update_request_body=request_body,
        user_id=user.user.id,
    )


@router.get(
    path="/reviews/{film_id:str}",
    response_model=schemas.ReviewUpdateResponseSchema,
    summary="create user's review record",
    description="An endpoint for handling user's review events",
    response_description="review record",
)
async def get_user_review(
    film_id: str,
    _: RateLimiterType,
    service: ReviewServiceType,
    user: UserToken,
) -> schemas.ReviewResponseSchema:
    return await service.get_user_review(
        film_id=film_id,
        user_id=user.user.id,
    )


@router.get(
    path="/reviews",
    response_model=Page[schemas.ReviewResponseSchema],
    summary="get film's review records",
    description="An endpoint for getting film's review records",
    response_description="review records",
)
async def get_reviews(
    _: RateLimiterType,
    service: ReviewServiceType,
    film_id: str,
    pagination_params: Params = Depends(Params),
) -> Page[schemas.ReviewResponseSchema]:
    return await service.get_films_reviews(
        film_id=film_id, pagination_params=pagination_params
    )
