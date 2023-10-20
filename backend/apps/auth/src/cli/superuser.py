from redis import asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth import dependencies as auth_depends
from src.auth.dependencies import get_auth_backend
from src.cli.database import get_async_db_session
from src.permissions.repositories import PostgresPermissionRepository
from src.permissions.services import PermissionsService
from src.settings.app import get_app_settings
from src.users import schemas as users_schemas
from src.users.repositories import (
    PostgresUserRepository,
    PostgresUserSigninHistoryRepository,
)
from src.users.service import UserService

settings = get_app_settings()


async def create_user_with_internal_permissions(
    user: auth_depends.UserSignUp,
) -> tuple[users_schemas.User, list[str]]:
    async with get_async_db_session() as db:
        user_service = await get_user_service(db)
        permission_service = await get_permission_service(db)

        created_user = await user_service.create_user(
            username=user.username,
            password=user.password,
            first_name=user.first_name,
            last_name=user.last_name,
        )
        all_permissions_db = await permission_service.create_internal_permissions()

        user_with_permissions = await user_service.assign_user_permissions(
            user_id=created_user.id,
            permission_ids=[permission.id for permission in all_permissions_db],
        )
    permissions_names = [permission.name for permission in all_permissions_db]
    return user_with_permissions, permissions_names


async def get_user_service(db: AsyncSession) -> UserService:
    auth_backend = await get_auth_backend(
        redis=aioredis.from_url(settings.redis.dsn, encoding="utf-8")
    )
    return UserService(
        user_repository=PostgresUserRepository(async_session=db),
        log_repository=PostgresUserSigninHistoryRepository(async_session=db),
        jwt_auth_backend=auth_backend,
    )


async def get_permission_service(db: AsyncSession) -> PermissionsService:
    return PermissionsService(
        permissions_repo=PostgresPermissionRepository(async_session=db)
    )
