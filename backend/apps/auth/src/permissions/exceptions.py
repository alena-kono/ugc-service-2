from http import HTTPStatus

from src.common.exceptions import BaseServiceError, ServiceAPIError


class PermissionPackageError(BaseServiceError):
    pass


class PermissionAPIError(PermissionPackageError, ServiceAPIError):
    pass


class PermissionNotGrantedError(PermissionAPIError):
    status_code = HTTPStatus.FORBIDDEN
    detail = "Permission to perform this operation is not granted"


class PermissionNameExistsError(PermissionAPIError):
    status_code = HTTPStatus.CONFLICT
    detail = "Permission with this name already exists"


class PermissionDoesNotExistError(PermissionAPIError):
    status_code = HTTPStatus.NOT_FOUND
    detail = "Permission with this id does not exist"


class PermissionInternalDoesNotExistError(PermissionAPIError):
    status_code = HTTPStatus.NOT_IMPLEMENTED
    detail = (
        "Permission required to perform this operation does not exist in the database"
    )
