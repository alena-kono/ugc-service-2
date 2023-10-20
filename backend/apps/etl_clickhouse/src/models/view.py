from datetime import datetime
from uuid import UUID

from src.models.base import AppBaseSchema

from pydantic import validator


class ViewMessage(AppBaseSchema):

    user_id: UUID

    film_id: UUID

    progress_sec: int

    timestamp: datetime

    @validator("timestamp", pre=True)
    def transform_to_utc_timestamp(cls, timestamp: float):
        return datetime.utcfromtimestamp(timestamp)
