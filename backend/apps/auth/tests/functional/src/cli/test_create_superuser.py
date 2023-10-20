import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth import dependencies as auth_depends
from src.auth.exceptions import UserUsernameExistsError
from src.cli.superuser import create_user_with_internal_permissions
from src.permissions import models as permissions_models
from src.permissions.enums import ServiceInternalPermission
from src.users import models as users_models

pytestmark = pytest.mark.asyncio


async def test_create_user_with_internal_permissions(
    db_session: AsyncSession,
) -> None:
    user_data = {
        "username": "superuser",
        "password": "Abcd1234!",
        "first_name": "adam",
        "last_name": "smith",
    }
    user_signup = auth_depends.UserSignUp(
        username=user_data["username"],
        password=user_data["password"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
    )
    (
        created_user,
        created_permissions_names,
    ) = await create_user_with_internal_permissions(user=user_signup)

    stmt = select(permissions_models.Permission).where(
        permissions_models.Permission.type == "internal"
    )
    result = await db_session.execute(stmt)
    internal_permissions_db = result.scalars().all()

    assert created_user.username == user_data["username"]
    assert created_user.first_name == user_data["first_name"]
    assert created_user.last_name == user_data["last_name"]

    assert {permission.name for permission in internal_permissions_db} == set(
        created_permissions_names
    )


async def test_create_user_with_few_existing_internal_permissions(
    db_session: AsyncSession,
) -> None:
    user_data = {
        "username": "superuser",
        "password": "Abcd1234!",
        "first_name": "adam",
        "last_name": "smith",
    }
    permission_0 = permissions_models.Permission(
        name=ServiceInternalPermission.permission_delete,
        type="internal",
    )
    permission_1 = permissions_models.Permission(
        name=ServiceInternalPermission.permission_update,
        type="internal",
    )
    db_session.add_all([permission_0, permission_1])
    await db_session.commit()

    user_signup = auth_depends.UserSignUp(
        username=user_data["username"],
        password=user_data["password"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
    )
    (
        created_user,
        created_permissions_names,
    ) = await create_user_with_internal_permissions(user=user_signup)

    stmt = select(permissions_models.Permission).where(
        permissions_models.Permission.type == "internal"
    )
    result = await db_session.execute(stmt)
    internal_permissions_db = result.scalars().all()

    assert created_user.username == user_data["username"]
    assert created_user.first_name == user_data["first_name"]
    assert created_user.last_name == user_data["last_name"]

    assert {permission.name for permission in internal_permissions_db} == set(
        created_permissions_names
    )


async def test_create_user_with_internal_permissions_user_already_exists(
    db_session: AsyncSession,
) -> None:
    user_data = {
        "username": "superuser",
        "password": "Abcd1234!",
        "first_name": "adam",
        "last_name": "smith",
    }
    user_0 = users_models.User(
        username=user_data["username"],
        password=user_data["password"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
    )
    permission_0 = permissions_models.Permission(
        name=ServiceInternalPermission.permission_delete,
        type="internal",
    )
    permission_1 = permissions_models.Permission(
        name=ServiceInternalPermission.permission_update,
        type="internal",
    )
    db_session.add_all([permission_0, permission_1, user_0])
    await db_session.commit()

    user_signup = auth_depends.UserSignUp(
        username=user_data["username"],
        password=user_data["password"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
    )
    with pytest.raises(UserUsernameExistsError):
        await create_user_with_internal_permissions(user=user_signup)
