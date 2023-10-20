import pydantic
from src.settings.base import BaseAppSettings


class PersonSettings(BaseAppSettings["PersonSettings"]):
    elastic_index: str = pydantic.Field(env="PERSON_ELASTIC_INDEX")
    cache_expire_in_seconds: int = pydantic.Field(
        env="PERSON_CACHE_EXPIRE_IN_SECONDS",
        default=300,
    )
