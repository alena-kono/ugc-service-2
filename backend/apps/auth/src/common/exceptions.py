from http import HTTPStatus
from uuid import UUID

from fastapi import HTTPException


class BaseServiceError(Exception):
    """Base class for all app custom exceptions"""

    pass


class APIErrorMixin(HTTPException):
    """REST API error mixin."""

    status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR
    detail: str = ""

    def __init__(
        self,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            status_code=self.status_code,
            detail=self.detail,
            headers=headers,
        )


class ServiceAPIError(APIErrorMixin, BaseServiceError):
    pass


class ResourceNotFound(HTTPException):
    resource_name = "Resource"

    def __init__(self, resource_id: UUID) -> None:
        super().__init__(
            HTTPStatus.NOT_FOUND,
            f"{self.resource_name} {resource_id} was not found",
        )
