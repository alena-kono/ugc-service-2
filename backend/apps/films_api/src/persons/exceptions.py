from src.common.exceptions import ResourceNotFound


class PersonNotFound(ResourceNotFound):
    resource_name = "Person"
