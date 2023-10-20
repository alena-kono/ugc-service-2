from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter
from src.auth.jwt import schemas as jwt_schemas
from src.common.dependencies import check_permission
from src.permissions import dependencies as permissions_depends
from src.permissions import enums as permissions_enums
from src.permissions import schemas as permissions_schemas
from src.permissions.services import IPermissionsService, get_permissions_service
from src.settings.app import get_app_settings

rl_settings = get_app_settings().rate_limiter

router = APIRouter()


@router.post(
    path="/",
    response_model=permissions_schemas.Permission,
    summary="",
    description="",
    response_description="",
)
async def create_permission(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=rl_settings.STANDARD_LIMIT.times,
                seconds=rl_settings.STANDARD_LIMIT.seconds,
            )
        ),
    ],
    create_permission: permissions_depends.PermissionCreate,
    service: Annotated[IPermissionsService, Depends(get_permissions_service)],
    access_token: Annotated[
        jwt_schemas.JWTDecoded,
        Depends(
            check_permission(
                permissions_enums.ServiceInternalPermission.permission_create
            )
        ),
    ],
) -> permissions_schemas.Permission:
    return await service.create_permission(permission=create_permission)


@router.delete(
    path="/{permission_id:uuid}",
    response_model=permissions_schemas.Permission,
    summary="",
    description="",
    response_description="",
)
async def delete_permission(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=rl_settings.STANDARD_LIMIT.times,
                seconds=rl_settings.STANDARD_LIMIT.seconds,
            )
        ),
    ],
    permission_id: UUID,
    service: Annotated[IPermissionsService, Depends(get_permissions_service)],
    access_token: Annotated[
        jwt_schemas.JWTDecoded,
        Depends(
            check_permission(
                permissions_enums.ServiceInternalPermission.permission_delete
            )
        ),
    ],
) -> permissions_schemas.Permission:
    return await service.delete_permission(permission_id)


@router.put(
    path="/{permission_id:uuid}",
    response_model=permissions_schemas.Permission,
    summary="",
    description="",
    response_description="",
)
async def update_permission(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=rl_settings.STANDARD_LIMIT.times,
                seconds=rl_settings.STANDARD_LIMIT.seconds,
            )
        ),
    ],
    permission_id: UUID,
    permission_update: permissions_depends.PermissionUpdate,
    service: Annotated[IPermissionsService, Depends(get_permissions_service)],
    access_token: Annotated[
        jwt_schemas.JWTDecoded,
        Depends(
            check_permission(
                permissions_enums.ServiceInternalPermission.permission_update
            )
        ),
    ],
) -> permissions_schemas.Permission:
    return await service.update_permission(permission_id, permission=permission_update)


@router.get(
    path="/",
    response_model=list[permissions_schemas.Permission],
    summary="",
    description="",
    response_description="",
)
async def get_permissions(
    rate_limiter: Annotated[
        RateLimiter,
        Depends(
            RateLimiter(
                times=rl_settings.STANDARD_LIMIT.times,
                seconds=rl_settings.STANDARD_LIMIT.seconds,
            )
        ),
    ],
    service: Annotated[IPermissionsService, Depends(get_permissions_service)],
    access_token: Annotated[
        jwt_schemas.JWTDecoded,
        Depends(
            check_permission(
                permissions_enums.ServiceInternalPermission.permission_read
            )
        ),
    ],
) -> list[permissions_schemas.Permission]:
    return await service.get_permissions()
