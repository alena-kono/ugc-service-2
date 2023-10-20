from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter
from fastapi_pagination import Page
from src.auth.jwt import schemas as jwt_schemas
from src.common.dependencies import check_permission
from src.permissions import enums as permissions_enums
from src.settings.app import get_app_settings
from src.users import dependencies as users_dependencies
from src.users import schemas as users_schemas
from src.users.dependencies import get_user_service
from src.users.service import IUserService

rl_settings = get_app_settings().rate_limiter

router = APIRouter()


@router.delete(
    path="/{user_id:uuid}",
    response_model=None,
    summary="",
    description="",
    response_description="",
)
async def delete_user(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=rl_settings.STANDARD_LIMIT.times,
                seconds=rl_settings.STANDARD_LIMIT.seconds,
            )
        ),
    ],
    user_id: UUID,
    service: Annotated[IUserService, Depends(get_user_service)],
    # _: Annotated[
    #     jwt_schemas.JWTDecoded,
    #     Depends(
    #         check_permission(permissions_enums.ServiceInternalPermission.user_update)
    #     ),
    # ],
) -> None:
    return await service.delete_user(user_id)


@router.get(
    path="/{user_id:uuid}",
    response_model=users_schemas.User,
    summary="",
    description="",
    response_description="",
)
async def get_user(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=rl_settings.STANDARD_LIMIT.times,
                seconds=rl_settings.STANDARD_LIMIT.seconds,
            )
        ),
    ],
    user_id: UUID,
    service: Annotated[IUserService, Depends(get_user_service)],
    _: Annotated[
        jwt_schemas.JWTDecoded,
        Depends(
            check_permission(permissions_enums.ServiceInternalPermission.user_read)
        ),
    ],
) -> users_schemas.User:
    return await service.get_user_by_id(user_id)


@router.get(
    path="/{user_id:uuid}/signin-history",
    response_model=Page[users_schemas.UserLoginRecord],
    summary="",
    description="",
    response_description="",
)
async def get_user_signin_history(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=rl_settings.STANDARD_LIMIT.times,
                seconds=rl_settings.STANDARD_LIMIT.seconds,
            )
        ),
    ],
    user_id: UUID,
    service: Annotated[IUserService, Depends(get_user_service)],
    _: Annotated[
        jwt_schemas.JWTDecoded,
        Depends(
            check_permission(permissions_enums.ServiceInternalPermission.user_read)
        ),
    ],
) -> Page[users_schemas.UserLoginRecord]:
    return await service.get_user_history(user_id)


@router.put(
    path="/{user_id:uuid}",
    response_model=users_schemas.User,
    summary="",
    description="",
    response_description="",
)
async def update_common_user_info(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=rl_settings.STANDARD_LIMIT.times,
                seconds=rl_settings.STANDARD_LIMIT.seconds,
            )
        ),
    ],
    user_id: UUID,
    user: users_dependencies.User,
    service: Annotated[IUserService, Depends(get_user_service)],
    _: Annotated[
        jwt_schemas.JWTDecoded,
        Depends(
            check_permission(permissions_enums.ServiceInternalPermission.user_update)
        ),
    ],
) -> users_schemas.User:
    return await service.update_user_common_info(
        user_id, user.username, user.first_name, user.last_name
    )


@router.post(
    path="/{user_id:uuid}/password-change",
    response_model=users_schemas.User,
    summary="",
    description="",
    response_description="",
)
async def change_password(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=rl_settings.STANDARD_LIMIT.times,
                seconds=rl_settings.STANDARD_LIMIT.seconds,
            )
        ),
    ],
    user_id: UUID,
    password_change: users_dependencies.PasswordChange,
    service: Annotated[IUserService, Depends(get_user_service)],
    _: Annotated[
        jwt_schemas.JWTDecoded,
        Depends(
            check_permission(permissions_enums.ServiceInternalPermission.user_update)
        ),
    ],
) -> users_schemas.User:
    return await service.change_user_password(
        user_id, password_change.old_password, password_change.password
    )


@router.post(
    path="/{user_id:uuid}/assign-permission",
    response_model=users_schemas.User,
    summary="",
    description="",
    response_description="",
)
async def assign_permission_for_user(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=rl_settings.STANDARD_LIMIT.times,
                seconds=rl_settings.STANDARD_LIMIT.seconds,
            )
        ),
    ],
    user_id: UUID,
    user_permission: users_dependencies.UserPermission,
    service: Annotated[IUserService, Depends(get_user_service)],
    _: Annotated[
        jwt_schemas.JWTDecoded,
        Depends(
            check_permission(permissions_enums.ServiceInternalPermission.user_update)
        ),
    ],
) -> users_schemas.User:
    return await service.assign_user_permission(user_id, user_permission.permission_id)


@router.post(
    path="/{user_id:uuid}/revoke-permission",
    response_model=users_schemas.User,
    summary="",
    description="",
    response_description="",
)
async def revoke_permission_from_user(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=rl_settings.STANDARD_LIMIT.times,
                seconds=rl_settings.STANDARD_LIMIT.seconds,
            )
        ),
    ],
    user_id: UUID,
    user_permission: users_dependencies.UserPermission,
    service: Annotated[IUserService, Depends(get_user_service)],
    _: Annotated[
        jwt_schemas.JWTDecoded,
        Depends(
            check_permission(permissions_enums.ServiceInternalPermission.user_update)
        ),
    ],
) -> users_schemas.User:
    return await service.revoke_user_permission(user_id, user_permission.permission_id)
