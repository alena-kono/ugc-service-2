import logging

from fastapi import APIRouter
from src.ugc.dependencies import EventServiceType, RateLimiterType, UserToken
from src.ugc.input_schemas import FilmProgressEvent, LikeEvent, CommentEvent
from src.ugc.output_schemas import FilmProgressSchema, LikeSchema, CommentSchema
from src.ugc.utils import TopicTypes


logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    path="/film-progress",
    response_model=FilmProgressSchema,
    summary="User's film progress events handler",
    description="An endpoint for handling user's film progress events",
    response_description="film progress record",
)
async def film_progress(
    _: RateLimiterType,
    service: EventServiceType,
    user: UserToken,
    event: FilmProgressEvent,
) -> FilmProgressSchema:
    return await service.handle_event(
        topic=TopicTypes.film_progress,
        input_schema=event,
        output_schema_class=FilmProgressSchema,
        user_id=user.user.id,
    )


@router.post(
    path="/comment",
    response_model=LikeSchema,
    summary="User's comment events handler",
    description="An endpoint for handling user's comment events",
    response_description="A comment record",
)
async def create_comment(
    _: RateLimiterType,
    service: EventServiceType,
    user: UserToken,
    event: LikeEvent,
) -> LikeSchema:
    return await service.handle_event(
        topic=TopicTypes.like,
        input_schema=event,
        output_schema_class=LikeSchema,
        user_id=user.user.id,
    )


@router.post(
    path="/like",
    response_model=None,
    summary="User's like events handler",
    description="An endpoint for handling user's like events",
    response_description="A comment record",
)
async def create_like(
    _: RateLimiterType,
    service: EventServiceType,
    user: UserToken,
    event: CommentEvent,
) -> CommentSchema:
    return await service.handle_event(
        topic=TopicTypes.comment,
        input_schema=event,
        output_schema_class=CommentSchema,
        user_id=user.user.id,
    )
