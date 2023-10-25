from src.utils.base_schema import BaseSchema


class InputBaseSchema(BaseSchema):
    film_id: str
    timestamp: float


class FilmProgressEvent(InputBaseSchema):
    progress_sec: int


class LikeEvent(InputBaseSchema):
    ...


class CommentEvent(InputBaseSchema):
    comment: str
