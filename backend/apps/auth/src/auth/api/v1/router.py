import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_limiter.depends import RateLimiter
from src.auth import dependencies as auth_depends
from src.auth.dependencies import (
    UserFingerprint,
    get_auth_backend,
    get_user_fingerprint,
    handle_access_token,
    handle_refresh_token,
)
from src.auth.exceptions import InvalidAccessTokenError, InvalidRefreshTokenError
from src.auth.jwt import schemas as jwt_schemas
from src.auth.jwt.backend import JWTAuthorizationBackend
from src.settings.app import get_app_settings
from src.users import schemas as users_schemas
from src.users.dependencies import get_user_service
from src.users.service import UserService

logger = logging.getLogger(__name__)

router = APIRouter()

rl_settings = get_app_settings().rate_limiter


@router.post(
    path="/signin",
    response_model=jwt_schemas.JWTCredentials,
    summary="User sign in",
    description="Sign in with username and password",
    response_description="Access and refresh tokens",
)
async def signin(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=rl_settings.STANDARD_LIMIT.times,
                seconds=rl_settings.STANDARD_LIMIT.seconds,
            )
        ),
    ],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: Annotated[UserService, Depends(get_user_service)],
    user_fingerprint: Annotated[UserFingerprint, Depends(get_user_fingerprint)],
) -> jwt_schemas.JWTCredentials:
    return await user_service.signin(
        user=auth_depends.UserSignIn(
            username=form_data.username,
            password=form_data.password,
        ),
        fingerprint=user_fingerprint,
    )


@router.post(
    path="/signup",
    response_model=users_schemas.User,
    summary="User sign up",
    description="Register a new user",
    response_description="Created user",
)
async def signup(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=rl_settings.STANDARD_LIMIT.times,
                seconds=rl_settings.STANDARD_LIMIT.seconds,
            )
        ),
    ],
    user: auth_depends.UserSignUp,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> users_schemas.User:
    return await user_service.signup(user)


@router.post(
    path="/signout",
    response_model=None,
    summary="User sign out",
    description="Sign out user by revoking credentials",
    response_description="Empty response",
)
async def signout(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=rl_settings.STANDARD_LIMIT.times,
                seconds=rl_settings.STANDARD_LIMIT.seconds,
            )
        ),
    ],
    access_token: Annotated[jwt_schemas.JWTDecoded, Depends(handle_access_token)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> None:
    return await user_service.signout(decoded_jwt=access_token)


@router.post(
    path="/token-verify",
    response_model=jwt_schemas.AccessTokenInfo,
    summary="Access token verification",
    description="Verify provided access token string",
    response_description="Status and provided access token",
)
async def verify_token(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=rl_settings.STANDARD_LIMIT.times,
                seconds=rl_settings.STANDARD_LIMIT.seconds,
            )
        ),
    ],
    client_access_token: Annotated[
        jwt_schemas.JWTDecoded, Depends(handle_access_token)
    ],
    access_token: auth_depends.AccessToken,
    auth_backend: Annotated[JWTAuthorizationBackend, Depends(get_auth_backend)],
) -> jwt_schemas.AccessTokenInfo:
    invalid_info = jwt_schemas.AccessTokenInfo(
        status=jwt_schemas.Status.INVALID,
        detail=jwt_schemas.StatusDetail.INVALID,
        provided_access_token=access_token.token_string,
    )
    try:
        decoded_access_token = await handle_access_token(
            access_token=access_token.token_string, auth_backend=auth_backend
        )
    except InvalidAccessTokenError:
        return invalid_info

    if not await auth_backend.verify_jwt_credentials_are_active(decoded_access_token):
        return invalid_info

    return jwt_schemas.AccessTokenInfo(
        status=jwt_schemas.Status.VALID,
        detail=jwt_schemas.StatusDetail.VALID,
        provided_access_token=access_token.token_string,
    )


@router.post(
    path="/token-refresh",
    response_model=jwt_schemas.JWTCredentials,
    summary="Refresh access token",
    description="Get new access token by providing the refresh token",
    response_description="New JWT credentials",
)
async def refresh_token(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=rl_settings.STANDARD_LIMIT.times,
                seconds=rl_settings.STANDARD_LIMIT.seconds,
            )
        ),
    ],
    access_token: Annotated[jwt_schemas.JWTDecoded, Depends(handle_access_token)],
    auth_backend: Annotated[JWTAuthorizationBackend, Depends(get_auth_backend)],
    refresh_token: Annotated[jwt_schemas.JWTDecoded, Depends(handle_refresh_token)],
) -> jwt_schemas.JWTCredentials:
    if access_token.user == refresh_token.user:
        return await auth_backend.refresh_jwt_credentials(decoded_token=access_token)
    logger.error("Refresh token error: user identities do not match")
    raise InvalidRefreshTokenError
