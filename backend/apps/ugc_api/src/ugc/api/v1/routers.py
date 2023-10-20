import logging

from fastapi import APIRouter, status
from fastapi.responses import ORJSONResponse
from src.ugc.dependencies import EventServiceType, RateLimiterType, UserToken
from src.ugc.schemas import FilmProgressEvent
from src.ugc.utils import TopicTypes

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    path="/film-progress",
    response_model=None,
    summary="User's film progress events handler",
    description="An endpoint for handling user's events",
    response_description="No content",
)
async def bookmarks_handler(
    _: RateLimiterType,
    service: EventServiceType,
    user: UserToken,
    event: FilmProgressEvent,
) -> ORJSONResponse:
    await service.handle_event(
        topic=TopicTypes.views,
        event=event,
        user_id=user.user.id,
    )
    return ORJSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)
