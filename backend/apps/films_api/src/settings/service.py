import pydantic
from src.settings.base import BaseAppSettings


class ServiceSettings(BaseAppSettings["ServiceSettings"]):
    name: str = pydantic.Field(env="SERVICE_NAME")
    host: str = pydantic.Field(env="SERVICE_HOST")
    port: int = pydantic.Field(env="SERVICE_PORT")

    description: str = pydantic.Field(
        env="SERVICE_DESCRIPTION",
        default="",
    )

    default_page_size: int = 50
