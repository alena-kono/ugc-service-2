import logging
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field, IPvAnyAddress
from redis.asyncio import Redis
from src.auth.exceptions import InvalidAccessTokenError, InvalidRefreshTokenError
from src.auth.jwt import schemas as jwt_schemas
from src.auth.jwt.backend import JWTAuthorizationBackend
from src.auth.jwt.exceptions import InvalidJWTError
from src.auth.jwt.service import validate_jwt
from src.auth.jwt.storage import JWTStorage
from src.common.cache import RedisCache
from src.common.database import get_redis
from src.users.settings import get_users_settings

logger = logging.getLogger(__name__)

users_settings = get_users_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/signin")


class UserFingerprint(BaseModel):
    ip_address: IPvAnyAddress | None
    user_agent: str


class UserSignIn(BaseModel):
    username: str
    password: str


class UserSignUp(BaseModel):
    username: str = Field(
        min_length=users_settings.username_min_length,
        max_length=users_settings.username_max_length,
        regex=users_settings.username_regex,
    )
    password: str = Field(
        min_length=users_settings.password_min_length,
        max_length=users_settings.password_max_length,
    )
    first_name: str = Field(
        min_length=users_settings.name_min_length,
        max_length=users_settings.name_max_length,
        regex=users_settings.name_regex,
    )
    last_name: str = Field(
        min_length=users_settings.name_min_length,
        max_length=users_settings.name_max_length,
        regex=users_settings.name_regex,
    )


class AccessToken(BaseModel):
    token_string: str = Field(regex=r"^(?:[\w-]*\.){2}[\w-]*$")


class RefreshToken(BaseModel):
    token_string: str = Field(regex=r"^(?:[\w-]*\.){2}[\w-]*$")


async def get_auth_backend(
    redis: Annotated[Redis, Depends(get_redis)]
) -> JWTAuthorizationBackend:
    """Initialize JWT authorization backend that uses Redis cache as a storage."""
    return JWTAuthorizationBackend(
        jwt_storage=JWTStorage(cache=RedisCache(redis_client=redis))
    )


async def handle_access_token(
    access_token: Annotated[str, Depends(oauth2_scheme)],
    auth_backend: Annotated[JWTAuthorizationBackend, Depends(get_auth_backend)],
) -> jwt_schemas.JWTDecoded:
    """Retrieve access token from `OAuth2PasswordBearer`, decode it
    and verify it is active (not revoked).
    """
    try:
        access_token_data = await validate_jwt(access_token)
    except InvalidJWTError:
        logger.error("Error when validating jwt's string signature or reserved claims")
        raise InvalidAccessTokenError

    if not access_token_data.type == "access":
        logger.error("Token type is %s, must be 'access'", access_token_data.type)
        raise InvalidAccessTokenError

    is_jwt_active = await auth_backend.verify_jwt_credentials_are_active(
        decoded_token=access_token_data
    )
    if not is_jwt_active:
        logger.error("Token is revoked (not active)")
        raise InvalidAccessTokenError

    return access_token_data


async def handle_refresh_token(
    refresh_token: RefreshToken,
    auth_backend: Annotated[JWTAuthorizationBackend, Depends(get_auth_backend)],
) -> jwt_schemas.JWTDecoded:
    """Retrieve access token from `RefreshToken`, decode it
    and verify it is active (not revoked).
    """
    try:
        refresh_token_data = await validate_jwt(refresh_token.token_string)
    except InvalidJWTError:
        logger.error("Error when validating jwt's string signature or reserved claims")
        raise InvalidRefreshTokenError

    if not refresh_token_data.type == "refresh":
        logger.error("Token type is %s, must be 'refresh'", refresh_token_data.type)
        raise InvalidRefreshTokenError

    is_jwt_active = await auth_backend.verify_jwt_credentials_are_active(
        decoded_token=refresh_token_data
    )
    if not is_jwt_active:
        logger.error("Token is revoked (not active)")
        raise InvalidRefreshTokenError

    return refresh_token_data


def get_user_fingerprint(request: Request) -> UserFingerprint:
    ip = None
    if client := request.client:
        ip = client.host
    return UserFingerprint(
        ip_address=ip,
        user_agent=request.headers.get("user-agent", ""),
    )
