from src.common.models import AppBaseModel


class Genre(AppBaseModel["Genre"]):
    name: str
    description: str | None
