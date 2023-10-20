from enum import StrEnum, auto, unique


@unique
class ServiceInternalPermission(StrEnum):
    """Internal permissions used to grant access to perform Service operations."""

    permission_read = auto()
    permission_update = auto()
    permission_create = auto()
    permission_delete = auto()
    user_read = auto()
    user_update = auto()
    user_write = auto()
    user_delete = auto()
    can_read_films = auto()
    can_read_genres = auto()
    can_read_persons = auto()
    user_can_create_content = auto()
