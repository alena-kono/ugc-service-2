import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.permissions import models as permissions_models
from src.permissions.enums import ServiceInternalPermission
from src.permissions.repositories import PostgresPermissionRepository

pytestmark = pytest.mark.asyncio


async def test_get_permission(
    db_session: AsyncSession,
) -> None:
    permission_model = permissions_models.Permission(
        name=ServiceInternalPermission.permission_update
    )

    db_session.add_all([permission_model])
    await db_session.commit()

    repo = PostgresPermissionRepository(db_session)
    permission = await repo.get(permission_model.id)

    assert permission is not None
    assert permission.id == permission_model.id
    assert permission.name == permission_model.name


async def test_update_permission(
    db_session: AsyncSession,
) -> None:
    expected_name = ServiceInternalPermission.permission_read

    permission_model = permissions_models.Permission(name="test_permission")
    db_session.add(permission_model)
    await db_session.commit()

    repo = PostgresPermissionRepository(db_session)
    permission = await repo.update(permission_model.id, name=expected_name)

    assert permission is not None
    assert permission.id == permission_model.id
    assert permission.name == expected_name


async def test_create_permission(
    db_session: AsyncSession,
) -> None:
    test_name = ServiceInternalPermission.permission_read
    repo = PostgresPermissionRepository(db_session)
    created_permission = await repo.create(name=test_name)

    permission = await repo.get(created_permission.id)

    assert permission.name == test_name  # type: ignore


async def test_bulk_create_permissions(
    db_session: AsyncSession,
) -> None:
    test_names = [
        ServiceInternalPermission.permission_read,
        ServiceInternalPermission.user_read,
    ]
    repo = PostgresPermissionRepository(db_session)
    created_permissions = await repo.create_bulk(
        names=[str(name.value) for name in test_names]
    )

    permissions_db = await repo.get_all()

    assert {permission.name for permission in created_permissions} == set(test_names)
    assert {permission.name for permission in permissions_db} == set(test_names)


async def test_delete_permission(
    db_session: AsyncSession,
) -> None:
    test_name = ServiceInternalPermission.permission_read

    repo = PostgresPermissionRepository(db_session)
    created_permission = await repo.create(name=test_name)

    await repo.remove(created_permission.id)
    permission = await repo.get(created_permission.id)
    assert permission is None
