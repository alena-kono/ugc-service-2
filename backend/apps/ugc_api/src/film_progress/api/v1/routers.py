import logging

from fastapi import APIRouter, Depends
from fastapi_pagination import Page, Params
from src.common.dependencies import RateLimiterType, UserToken
from src.film_progress import schemas
from src.film_progress.dependencies import FilmServiceType

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    path="/films-progresses",
    response_model=schemas.FilmProgressCreateResponseSchema,
    summary="create user's film progress record",
    description="An endpoint for handling user's film progress events",
    response_description="film progress record",
)
async def film_progress(
    _: RateLimiterType,
    service: FilmServiceType,
    user: UserToken,
    request_body: schemas.FilmProgressCreateRequestSchema,
) -> schemas.FilmProgressCreateResponseSchema:
    return await service.create_film_progress(
        create_request_body=request_body,
        user_id=user.user.id,
    )


@router.get(
    path="/films-progresses",
    response_model=Page[schemas.FilmProgressCreateResponseSchema],
    summary="get user's unfinished films",
    description="An endpoint for getting user's unfinished films",
    response_description="page of unfinished films",
)
async def get_unfinished_films(
    _: RateLimiterType,
    service: FilmServiceType,
    user: UserToken,
    pagination_params: Params = Depends(),
) -> Page[schemas.FilmProgressResponseSchema]:
    return await service.get_unfinished_films(
        user_id=user.user.id, pagination_params=pagination_params
    )
