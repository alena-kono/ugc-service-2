from datetime import datetime
from uuid import UUID

from pydantic import validator
from src.models.base import AppBaseSchema


class ViewMessage(AppBaseSchema):
    user_id: UUID

    film_id: UUID

    progress_sec: int

    timestamp: datetime

    @validator("timestamp", pre=True)
    @classmethod
    def transform_to_utc_timestamp(cls, timestamp: float):
        return datetime.utcfromtimestamp(timestamp)
