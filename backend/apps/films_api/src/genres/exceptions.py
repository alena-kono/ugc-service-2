from src.common.exceptions import ResourceNotFound


class GenreNotFound(ResourceNotFound):
    resource_name = "Genre"
