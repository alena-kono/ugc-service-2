from enum import StrEnum, auto, unique


@unique
class TopicTypes(StrEnum):
    film_progress = auto()
    like = auto()
    comment = auto()
