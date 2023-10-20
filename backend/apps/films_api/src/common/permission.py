from enum import StrEnum, auto


class Permissions(StrEnum):
    can_read_films = auto()
    can_read_genres = auto()
    can_read_persons = auto()
