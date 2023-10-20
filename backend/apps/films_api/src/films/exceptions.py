from src.common.exceptions import ResourceNotFound


class FilmNotFound(ResourceNotFound):
    resource_name = "Film"
