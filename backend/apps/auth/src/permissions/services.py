from abc import ABC, abstractmethod
from uuid import UUID

import sqlalchemy.exc as sqlalchemy_exc
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.database import get_db
from src.permissions import dependencies as permissions_depends
from src.permissions import schemas as permissions_schemas
from src.permissions.enums import ServiceInternalPermission
from src.permissions.exceptions import (
    PermissionDoesNotExistError,
    PermissionNameExistsError,
)
from src.permissions.repositories import (
    PermissionRepository,
    PostgresPermissionRepository,
)


class IPermissionsService(ABC):
    @abstractmethod
    async def create_permission(
        self,
        permission: permissions_depends.PermissionCreate,
    ) -> permissions_schemas.Permission:
        ...

    @abstractmethod
    async def delete_permission(
        self, permission_id: UUID
    ) -> permissions_schemas.Permission:
        ...

    @abstractmethod
    async def update_permission(
        self, permission_id: UUID, permission: permissions_depends.PermissionUpdate
    ) -> permissions_schemas.Permission:
        ...

    @abstractmethod
    async def get_permissions(self) -> list[permissions_schemas.Permission]:
        ...

    @abstractmethod
    async def get_permission_by_name(
        self, permission_name: str
    ) -> permissions_schemas.Permission | None:
        ...


class PermissionsService(IPermissionsService):
    def __init__(self, permissions_repo: PermissionRepository) -> None:
        self.repo = permissions_repo

    async def create_permission(
        self,
        permission: permissions_depends.PermissionCreate,
    ) -> permissions_schemas.Permission:
        try:
            permission_db = await self.repo.create(name=permission.name)
        except sqlalchemy_exc.IntegrityError:
            raise PermissionNameExistsError

        return permission_db

    async def delete_permission(
        self, permission_id: UUID
    ) -> permissions_schemas.Permission:
        permission_schema = await self.repo.get(permission_id)
        if permission_schema is None:
            raise PermissionDoesNotExistError

        await self.repo.remove(permission_id)
        return permission_schema

    async def update_permission(
        self, permission_id: UUID, permission: permissions_depends.PermissionUpdate
    ) -> permissions_schemas.Permission:
        if permission_db := await self.repo.get(permission_id):
            return await self.repo.update(
                permission_id=permission_db.id, name=permission.name
            )
        raise PermissionDoesNotExistError

    async def get_permissions(self) -> list[permissions_schemas.Permission]:
        return await self.repo.get_all()

    async def get_permission_by_name(
        self, permission_name: str
    ) -> permissions_schemas.Permission | None:
        return await self.repo.get_by_name(permission_name)

    async def get_internal_permissions(self) -> list[permissions_schemas.Permission]:
        return await self.repo.filter_by(type="internal")

    async def create_internal_permissions(self) -> list[permissions_schemas.Permission]:
        existing_permissions = await self.get_internal_permissions()
        existing_permissions_names = [
            permission.name for permission in existing_permissions
        ]

        required_permissions_names = await self._get_internal_permissions_names()

        permissions_names_to_create = list(
            set(required_permissions_names).difference(set(existing_permissions_names))
        )

        created_permissions = await self.repo.create_bulk(
            names=permissions_names_to_create, type_="internal"
        )

        return existing_permissions + created_permissions

    async def _get_internal_permissions_names(self) -> list[str]:
        return [str(permission.value) for permission in ServiceInternalPermission]


async def get_permissions_service(
    db_session: AsyncSession = Depends(get_db),
) -> IPermissionsService:
    return PermissionsService(
        permissions_repo=PostgresPermissionRepository(async_session=db_session)
    )
