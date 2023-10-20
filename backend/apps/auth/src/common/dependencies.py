from typing import Callable, Coroutine

from fastapi import Depends
from src.auth.dependencies import handle_access_token
from src.auth.jwt import schemas as jwt_schemas
from src.permissions import enums as permissions_enums
from src.permissions.exceptions import PermissionNotGrantedError

CheckPermissionsType = Callable[
    [jwt_schemas.JWTDecoded], Coroutine[None, None, jwt_schemas.JWTDecoded]
]


def check_permission(
    permission_name: permissions_enums.ServiceInternalPermission,
) -> CheckPermissionsType:
    async def _check_permission(
        access_token: jwt_schemas.JWTDecoded = Depends(handle_access_token),
    ) -> jwt_schemas.JWTDecoded:
        if permission_name not in access_token.user.permissions:
            raise PermissionNotGrantedError

        return access_token

    return _check_permission
