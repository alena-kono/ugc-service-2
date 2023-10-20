from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.permissions import models as permissions_models
from src.permissions import schemas as permissions_schemas


class PermissionRepository(ABC):
    @abstractmethod
    async def get(self, permission_id: UUID) -> permissions_schemas.Permission | None:
        ...

    @abstractmethod
    async def get_by_name(
        self,
        name: str,
    ) -> permissions_schemas.Permission | None:
        ...

    @abstractmethod
    async def get_all(self) -> list[permissions_schemas.Permission]:
        ...

    @abstractmethod
    async def update(
        self,
        permission_id: UUID,
        name: str,
    ) -> permissions_schemas.Permission:
        ...

    @abstractmethod
    async def create(self, name: str) -> permissions_schemas.Permission:
        ...

    @abstractmethod
    async def create_bulk(
        self,
        names: list[str],
        type_: str | None = None,
    ) -> list[permissions_schemas.Permission]:
        ...

    @abstractmethod
    async def filter_by(self, **kwargs: Any) -> list[permissions_schemas.Permission]:
        ...

    @abstractmethod
    async def remove(self, permission_id: UUID) -> None:
        ...


class PostgresPermissionRepository(PermissionRepository):
    def __init__(self, async_session: AsyncSession) -> None:
        self.async_session = async_session

    async def get(self, permission_id: UUID) -> permissions_schemas.Permission | None:
        stmt = select(permissions_models.Permission).where(
            permissions_models.Permission.id == permission_id
        )
        result = await self.async_session.execute(stmt)
        permission = result.scalar()

        if permission is None:
            return None

        return permissions_schemas.Permission.from_orm(permission)

    async def get_by_name(self, name: str) -> permissions_schemas.Permission | None:
        stmt = select(permissions_models.Permission).where(
            permissions_models.Permission.name == name
        )
        result = await self.async_session.execute(stmt)
        permission = result.scalar()

        if permission is None:
            return None

        return permissions_schemas.Permission.from_orm(permission)

    async def get_all(self) -> list[permissions_schemas.Permission]:
        stmt = select(permissions_models.Permission)
        result = await self.async_session.execute(stmt)
        permissions = result.scalars()

        schemas = [
            permissions_schemas.Permission.from_orm(permission)
            for permission in permissions
        ]

        return schemas

    async def update(
        self,
        permission_id: UUID,
        name: str,
    ) -> permissions_schemas.Permission:
        stmt = (
            update(permissions_models.Permission)
            .where(permissions_models.Permission.id == permission_id)
            .values(name=name)
        )
        await self.async_session.execute(stmt)

        return await self.get(permission_id)  # type: ignore

    async def create(self, name: str) -> permissions_schemas.Permission:
        permission = permissions_models.Permission(name=name)
        self.async_session.add(permission)
        await self.async_session.commit()

        return await self.get(permission.id)  # type: ignore

    async def create_bulk(
        self,
        names: list[str],
        type_: str | None = None,
    ) -> list[permissions_schemas.Permission]:
        permissions = [
            permissions_models.Permission(name=name, type=type_) for name in names
        ]

        self.async_session.add_all(permissions)
        await self.async_session.commit()

        return [
            permissions_schemas.Permission.from_orm(permission)
            for permission in permissions
        ]

    async def filter_by(self, **kwargs: Any) -> list[permissions_schemas.Permission]:
        stmt = (
            select(permissions_models.Permission)
            .options(selectinload(permissions_models.Permission.users))
            .filter_by(**kwargs)
        )
        result = await self.async_session.execute(stmt)
        permissions = result.scalars().all()

        return [
            permissions_schemas.Permission.from_orm(permission)
            for permission in permissions
        ]

    async def remove(self, permission_id: UUID) -> None:
        stmt = delete(permissions_models.Permission).where(
            permissions_models.Permission.id == str(permission_id)
        )
        await self.async_session.execute(stmt)
        await self.async_session.commit()
