from http import HTTPStatus

from src.common.exceptions import BaseServiceError, ServiceAPIError


class AuthError(BaseServiceError):
    pass


class AuthAPIError(ServiceAPIError):
    pass


class InvalidAccessTokenError(AuthAPIError):
    status_code = HTTPStatus.UNAUTHORIZED
    detail = "Invalid access token"


class InvalidRefreshTokenError(AuthAPIError):
    status_code = HTTPStatus.CONFLICT
    detail = "Invalid refresh token"


class UserInvalidCredentialsError(AuthAPIError):
    status_code = HTTPStatus.UNAUTHORIZED
    detail = "Invalid user credentials"


class UserUsernameExistsError(AuthAPIError):
    status_code = HTTPStatus.CONFLICT
    detail = "User with this username already exists"
