import pydantic
from src.settings.base import BaseAppSettings


class ServiceSettings(BaseAppSettings):
    name: str = pydantic.Field(env="SERVICE_NAME")
    host: str = pydantic.Field(env="SERVICE_HOST")
    port: int = pydantic.Field(env="SERVICE_PORT")
    debug: bool = pydantic.Field(env="SERVICE_DEBUG", default=False)

    description: str = pydantic.Field(
        env="SERVICE_DESCRIPTION",
        default="",
    )
