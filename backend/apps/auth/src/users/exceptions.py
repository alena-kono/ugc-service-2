from http import HTTPStatus

from src.common.exceptions import ResourceNotFound, ServiceAPIError


class UserDoesNotExistError(ResourceNotFound):
    resource_name: str = "User"


class UserPermissionError(ServiceAPIError):
    status_code: int = HTTPStatus.UNPROCESSABLE_ENTITY


class UserUpdateError(ServiceAPIError):
    status_code: int = HTTPStatus.UNPROCESSABLE_ENTITY
