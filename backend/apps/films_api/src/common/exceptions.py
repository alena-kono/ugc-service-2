from http import HTTPStatus
from uuid import UUID

from fastapi import HTTPException


class AppBaseError(Exception):
    pass


class ResourceNotFound(HTTPException):
    resource_name = "Resource"

    def __init__(self, resource_id: UUID) -> None:
        super().__init__(
            HTTPStatus.NOT_FOUND,
            f"{self.resource_name} {resource_id} was not found",
        )


class ElasticsearchRepositoryError(AppBaseError):
    pass


class AuthIsUnavailableError(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            HTTPStatus.SERVICE_UNAVAILABLE,
            "Authorization service is unavailable. Please try again later.",
        )
