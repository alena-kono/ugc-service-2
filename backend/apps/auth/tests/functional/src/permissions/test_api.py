from datetime import datetime
from http import HTTPStatus
from uuid import UUID

import orjson
import pytest
from httpx import AsyncClient
from passlib.hash import pbkdf2_sha256
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.permissions import models as permissions_models
from src.users import models as users_models

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "permission_name",
    [
        "watch_premium",
        "user_create",
        "12345",
        123,
        0.25,
    ],
)
async def test_create_permission_valid_name(
    db_session: AsyncSession,
    client: AsyncClient,
    permission_name: str,
) -> None:
    permission_0 = permissions_models.Permission(
        id=UUID("743a1c54-aa4c-4576-bf77-b9a0ed7d819b"),
        name="permission_create",
    )
    user_0 = users_models.User(
        id=UUID("5b90edb4-ac98-4053-ac8b-93203aa8a039"),
        username="superuser",
        password=pbkdf2_sha256.hash("Ab1234567!"),
        first_name="adam",
        last_name="smith",
    )
    db_session.add_all([permission_0, user_0])
    await db_session.commit()

    user_permission_0 = permissions_models.UsersPermissions(
        permission=permission_0, user=user_0
    )
    db_session.add_all([user_permission_0])
    await db_session.commit()

    # Sign in first
    response_signin = await client.post(
        "/api/v1/auth/signin",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        content="username=superuser&password=Ab1234567!",
    )
    assert response_signin.status_code == HTTPStatus.OK

    access_token = response_signin.json()["access_token"]

    # Test api endpoint
    response = await client.post(
        "/api/v1/permissions/",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        content=orjson.dumps({"name": permission_name}),
    )
    assert response.status_code == HTTPStatus.OK

    data = response.json()
    assert data is not None

    assert set(data.keys()) == {"created_at", "modified_at", "id", "name"}
    assert data["name"] == str(permission_name)

    # Check db
    stmt = select(permissions_models.Permission).where(
        permissions_models.Permission.name == str(permission_name)
    )
    result = await db_session.execute(stmt)
    permission_db = result.scalar()

    assert permission_db is not None


async def test_create_permission_already_exists(
    db_session: AsyncSession,
    client: AsyncClient,
) -> None:
    permission_name = "permission_create"
    permission_0 = permissions_models.Permission(
        id=UUID("743a1c54-aa4c-4576-bf77-b9a0ed7d819b"),
        name=permission_name,
    )
    user_0 = users_models.User(
        id=UUID("5b90edb4-ac98-4053-ac8b-93203aa8a039"),
        username="superuser",
        password=pbkdf2_sha256.hash("Ab1234567!"),
        first_name="adam",
        last_name="smith",
    )
    db_session.add_all([permission_0, user_0])
    await db_session.commit()

    user_permission_0 = permissions_models.UsersPermissions(
        permission=permission_0, user=user_0
    )
    db_session.add_all([user_permission_0])
    await db_session.commit()

    # Sign in first
    response_signin = await client.post(
        "/api/v1/auth/signin",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        content="username=superuser&password=Ab1234567!",
    )
    assert response_signin.status_code == HTTPStatus.OK

    access_token = response_signin.json()["access_token"]

    # Test api endpoint
    response = await client.post(
        "/api/v1/permissions/",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        content=orjson.dumps({"name": permission_name}),
    )
    assert response.status_code == HTTPStatus.CONFLICT

    data = response.json()
    assert data == {"detail": "Permission with this name already exists"}


@pytest.mark.parametrize(
    "permission_name",
    [
        "a",
        "ab",
        "",
    ],
)
async def test_create_permission_invalid_name(
    db_session: AsyncSession,
    client: AsyncClient,
    permission_name: str,
) -> None:
    permission_0 = permissions_models.Permission(
        id=UUID("743a1c54-aa4c-4576-bf77-b9a0ed7d819b"),
        name="permission_create",
    )
    user_0 = users_models.User(
        id=UUID("5b90edb4-ac98-4053-ac8b-93203aa8a039"),
        username="superuser",
        password=pbkdf2_sha256.hash("Ab1234567!"),
        first_name="adam",
        last_name="smith",
    )
    db_session.add_all([permission_0, user_0])
    await db_session.commit()

    user_permission_0 = permissions_models.UsersPermissions(
        permission=permission_0, user=user_0
    )
    db_session.add_all([user_permission_0])
    await db_session.commit()

    # Sign in first
    response_signin = await client.post(
        "/api/v1/auth/signin",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        content="username=superuser&password=Ab1234567!",
    )
    assert response_signin.status_code == HTTPStatus.OK

    access_token = response_signin.json()["access_token"]

    # Test api endpoint
    response = await client.post(
        "/api/v1/permissions/",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        content=orjson.dumps({"name": permission_name}),
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    # Check db
    stmt = select(permissions_models.Permission).where(
        permissions_models.Permission.name == str(permission_name)
    )
    result = await db_session.execute(stmt)
    permission_db = result.scalar()

    assert permission_db is None


async def test_create_permission_forbidden(
    db_session: AsyncSession,
    client: AsyncClient,
) -> None:
    permission_0 = permissions_models.Permission(
        id=UUID("743a1c54-aa4c-4576-bf77-b9a0ed7d819b"),
        name="permission_create",
    )
    user_0 = users_models.User(
        id=UUID("5b90edb4-ac98-4053-ac8b-93203aa8a039"),
        username="superuser",
        password=pbkdf2_sha256.hash("Ab1234567!"),
        first_name="adam",
        last_name="smith",
    )
    permission_to_test = permissions_models.Permission(
        id=UUID("15765172-4386-4d51-b4f2-af68bb82a888"),
        name="read_movies_list",
    )
    db_session.add_all([permission_to_test, permission_0, user_0])
    await db_session.commit()

    user_permission_0 = permissions_models.UsersPermissions(
        permission=permission_to_test, user=user_0
    )
    db_session.add_all([user_permission_0])
    await db_session.commit()

    # Sign in first
    response_signin = await client.post(
        "/api/v1/auth/signin",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        content="username=superuser&password=Ab1234567!",
    )
    assert response_signin.status_code == HTTPStatus.OK

    access_token = response_signin.json()["access_token"]

    # Test api endpoint
    response = await client.post(
        "/api/v1/permissions/",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        content=orjson.dumps({"name": "new"}),
    )

    assert response.status_code == HTTPStatus.FORBIDDEN

    data = response.json()
    assert data == {"detail": "Permission to perform this operation is not granted"}


async def test_delete_permission_exists(
    db_session: AsyncSession,
    client: AsyncClient,
) -> None:
    permission_0 = permissions_models.Permission(
        id=UUID("743a1c54-aa4c-4576-bf77-b9a0ed7d819b"),
        name="permission_delete",
    )
    user_0 = users_models.User(
        id=UUID("5b90edb4-ac98-4053-ac8b-93203aa8a039"),
        username="superuser",
        password=pbkdf2_sha256.hash("Ab1234567!"),
        first_name="adam",
        last_name="smith",
    )
    permission_to_delete = permissions_models.Permission(
        id=UUID("2b2a78c1-5552-4c4e-8d63-789e775994c7"),
        name="test",
    )
    db_session.add_all([permission_0, user_0, permission_to_delete])
    await db_session.commit()

    user_permission_0 = permissions_models.UsersPermissions(
        permission=permission_0, user=user_0
    )
    db_session.add_all([user_permission_0])
    await db_session.commit()

    # Sign in first
    response_signin = await client.post(
        "/api/v1/auth/signin",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        content="username=superuser&password=Ab1234567!",
    )
    assert response_signin.status_code == HTTPStatus.OK

    access_token = response_signin.json()["access_token"]

    # Test api endpoint
    response = await client.delete(
        f"/api/v1/permissions/{permission_to_delete.id}",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )
    assert response.status_code == HTTPStatus.OK

    data = response.json()
    assert set(data.keys()) == {"created_at", "modified_at", "id", "name"}
    assert data["id"] == str(permission_to_delete.id)
    assert data["name"] == str(permission_to_delete.name)

    # Check db
    stmt = select(permissions_models.Permission).where(
        permissions_models.Permission.id == permission_to_delete.id
    )
    result = await db_session.execute(stmt)
    permission_db = result.scalar()

    assert permission_db is None


async def test_delete_permission_does_not_exist(
    db_session: AsyncSession,
    client: AsyncClient,
) -> None:
    non_existent_permission_id = UUID("2b2a78c1-5552-4c4e-8d63-789e775994c7")

    permission_0 = permissions_models.Permission(
        id=UUID("743a1c54-aa4c-4576-bf77-b9a0ed7d819b"),
        name="permission_delete",
    )
    user_0 = users_models.User(
        id=UUID("5b90edb4-ac98-4053-ac8b-93203aa8a039"),
        username="superuser",
        password=pbkdf2_sha256.hash("Ab1234567!"),
        first_name="adam",
        last_name="smith",
    )
    db_session.add_all([permission_0, user_0])
    await db_session.commit()

    user_permission_0 = permissions_models.UsersPermissions(
        permission=permission_0, user=user_0
    )
    db_session.add_all([user_permission_0])
    await db_session.commit()

    # Sign in first
    response_signin = await client.post(
        "/api/v1/auth/signin",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        content="username=superuser&password=Ab1234567!",
    )
    assert response_signin.status_code == HTTPStatus.OK

    access_token = response_signin.json()["access_token"]

    # Test api endpoint
    response = await client.delete(
        f"/api/v1/permissions/{non_existent_permission_id}",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND

    data = response.json()
    assert data == {"detail": "Permission with this id does not exist"}


async def test_delete_permission_forbidden(
    db_session: AsyncSession,
    client: AsyncClient,
) -> None:
    permission_0 = permissions_models.Permission(
        id=UUID("743a1c54-aa4c-4576-bf77-b9a0ed7d819b"),
        name="permission_delete",
    )
    user_0 = users_models.User(
        id=UUID("5b90edb4-ac98-4053-ac8b-93203aa8a039"),
        username="superuser",
        password=pbkdf2_sha256.hash("Ab1234567!"),
        first_name="adam",
        last_name="smith",
    )
    permission_to_test = permissions_models.Permission(
        id=UUID("15765172-4386-4d51-b4f2-af68bb82a888"),
        name="read_movies_list",
    )
    db_session.add_all([permission_to_test, permission_0, user_0])
    await db_session.commit()

    user_permission_0 = permissions_models.UsersPermissions(
        permission=permission_to_test, user=user_0
    )
    db_session.add_all([user_permission_0])
    await db_session.commit()

    # Sign in first
    response_signin = await client.post(
        "/api/v1/auth/signin",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        content="username=superuser&password=Ab1234567!",
    )
    assert response_signin.status_code == HTTPStatus.OK

    access_token = response_signin.json()["access_token"]

    # Test api endpoint
    response = await client.delete(
        f"/api/v1/permissions/{permission_to_test.id}",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN

    data = response.json()
    assert data == {"detail": "Permission to perform this operation is not granted"}


@pytest.mark.parametrize(
    "permission_name",
    [
        "watch_premium",
        "user_create",
        "12345",
        123,
        0.25,
    ],
)
async def test_update_permission_exists(
    db_session: AsyncSession,
    client: AsyncClient,
    permission_name: str,
) -> None:
    permission_0 = permissions_models.Permission(
        id=UUID("743a1c54-aa4c-4576-bf77-b9a0ed7d819b"),
        name="permission_update",
    )
    user_0 = users_models.User(
        id=UUID("5b90edb4-ac98-4053-ac8b-93203aa8a039"),
        username="superuser",
        password=pbkdf2_sha256.hash("Ab1234567!"),
        first_name="adam",
        last_name="smith",
    )
    permission_to_update = permissions_models.Permission(
        id=UUID("2b2a78c1-5552-4c4e-8d63-789e775994c7"),
        name=permission_name,
        created_at=datetime(year=2023, month=1, day=1),
    )
    db_session.add_all([permission_0, user_0, permission_to_update])
    await db_session.commit()

    user_permission_0 = permissions_models.UsersPermissions(
        permission=permission_0, user=user_0
    )
    db_session.add_all([user_permission_0])
    await db_session.commit()

    # Sign in first
    response_signin = await client.post(
        "/api/v1/auth/signin",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        content="username=superuser&password=Ab1234567!",
    )
    assert response_signin.status_code == HTTPStatus.OK

    access_token = response_signin.json()["access_token"]

    # Test api endpoint
    response = await client.put(
        f"/api/v1/permissions/{permission_to_update.id}",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        content=orjson.dumps({"name": permission_name}),
    )
    assert response.status_code == HTTPStatus.OK

    data = response.json()
    assert set(data.keys()) == {"created_at", "modified_at", "id", "name"}
    assert data["id"] == str(permission_to_update.id)
    assert data["name"] == str(permission_to_update.name)

    # Check db
    stmt = select(permissions_models.Permission).where(
        permissions_models.Permission.id == permission_to_update.id
    )
    result = await db_session.execute(stmt)
    permission_db = result.scalar()

    assert permission_db is not None
    assert permission_db.id == permission_to_update.id
    assert permission_db.name == permission_to_update.name
    assert permission_db.created_at == permission_to_update.created_at
    assert permission_db.created_at < permission_db.modified_at


async def test_update_permission_does_not_exist(
    db_session: AsyncSession,
    client: AsyncClient,
) -> None:
    non_existent_permission_id = UUID("2b2a78c1-5552-4c4e-8d63-789e775994c7")

    permission_0 = permissions_models.Permission(
        id=UUID("743a1c54-aa4c-4576-bf77-b9a0ed7d819b"),
        name="permission_update",
    )
    user_0 = users_models.User(
        id=UUID("5b90edb4-ac98-4053-ac8b-93203aa8a039"),
        username="superuser",
        password=pbkdf2_sha256.hash("Ab1234567!"),
        first_name="adam",
        last_name="smith",
    )
    db_session.add_all([permission_0, user_0])
    await db_session.commit()

    user_permission_0 = permissions_models.UsersPermissions(
        permission=permission_0, user=user_0
    )
    db_session.add_all([user_permission_0])
    await db_session.commit()

    # Sign in first
    response_signin = await client.post(
        "/api/v1/auth/signin",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        content="username=superuser&password=Ab1234567!",
    )
    assert response_signin.status_code == HTTPStatus.OK

    access_token = response_signin.json()["access_token"]

    # Test api endpoint
    response = await client.put(
        f"/api/v1/permissions/{non_existent_permission_id}",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        content=orjson.dumps({"name": "new_perm_name"}),
    )
    assert response.status_code == HTTPStatus.NOT_FOUND

    data = response.json()
    assert data == {"detail": "Permission with this id does not exist"}


@pytest.mark.parametrize(
    "permission_name",
    [
        "a",
        "ab",
        "",
    ],
)
async def test_update_permission_invalid_data(
    db_session: AsyncSession,
    client: AsyncClient,
    permission_name: str,
) -> None:
    permission_0 = permissions_models.Permission(
        id=UUID("743a1c54-aa4c-4576-bf77-b9a0ed7d819b"),
        name="permission_update",
    )
    user_0 = users_models.User(
        id=UUID("5b90edb4-ac98-4053-ac8b-93203aa8a039"),
        username="superuser",
        password=pbkdf2_sha256.hash("Ab1234567!"),
        first_name="adam",
        last_name="smith",
    )
    permission_to_update = permissions_models.Permission(
        id=UUID("2b2a78c1-5552-4c4e-8d63-789e775994c7"),
        name="old",
    )
    db_session.add_all([permission_0, user_0, permission_to_update])
    await db_session.commit()

    user_permission_0 = permissions_models.UsersPermissions(
        permission=permission_0, user=user_0
    )
    db_session.add_all([user_permission_0])
    await db_session.commit()

    # Sign in first
    response_signin = await client.post(
        "/api/v1/auth/signin",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        content="username=superuser&password=Ab1234567!",
    )
    assert response_signin.status_code == HTTPStatus.OK

    access_token = response_signin.json()["access_token"]

    # Test api endpoint
    response = await client.put(
        f"/api/v1/permissions/{permission_to_update.id}",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        content=orjson.dumps({"name": permission_name}),
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    # Check db
    stmt = select(permissions_models.Permission).where(
        permissions_models.Permission.name == str(permission_name)
    )
    result = await db_session.execute(stmt)
    permission = result.scalar()

    assert permission is None


async def test_update_permission_forbidden(
    db_session: AsyncSession,
    client: AsyncClient,
) -> None:
    permission_0 = permissions_models.Permission(
        id=UUID("743a1c54-aa4c-4576-bf77-b9a0ed7d819b"),
        name="permission_update",
    )
    user_0 = users_models.User(
        id=UUID("5b90edb4-ac98-4053-ac8b-93203aa8a039"),
        username="superuser",
        password=pbkdf2_sha256.hash("Ab1234567!"),
        first_name="adam",
        last_name="smith",
    )
    permission_to_test = permissions_models.Permission(
        id=UUID("15765172-4386-4d51-b4f2-af68bb82a888"),
        name="read_movies_list",
    )
    db_session.add_all([permission_to_test, permission_0, user_0])
    await db_session.commit()

    user_permission_0 = permissions_models.UsersPermissions(
        permission=permission_to_test, user=user_0
    )
    db_session.add_all([user_permission_0])
    await db_session.commit()

    # Sign in first
    response_signin = await client.post(
        "/api/v1/auth/signin",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        content="username=superuser&password=Ab1234567!",
    )
    assert response_signin.status_code == HTTPStatus.OK

    access_token = response_signin.json()["access_token"]

    # Test api endpoint
    response = await client.put(
        f"/api/v1/permissions/{permission_to_test.id}",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        content=orjson.dumps({"name": "new"}),
    )

    assert response.status_code == HTTPStatus.FORBIDDEN

    data = response.json()
    assert data == {"detail": "Permission to perform this operation is not granted"}


@pytest.mark.parametrize(
    "permissions_names",
    [
        ["test", "new", "all"],
        ["test", "all"],
        ["test"],
        [],
    ],
)
async def test_get_permissions(
    db_session: AsyncSession,
    client: AsyncClient,
    permissions_names: list[str | None],
) -> None:
    permission_0 = permissions_models.Permission(
        id=UUID("743a1c54-aa4c-4576-bf77-b9a0ed7d819b"),
        name="permission_read",
    )
    user_0 = users_models.User(
        id=UUID("5b90edb4-ac98-4053-ac8b-93203aa8a039"),
        username="superuser",
        password=pbkdf2_sha256.hash("Ab1234567!"),
        first_name="adam",
        last_name="smith",
    )
    user_models_to_db = [user_0]
    permission_models_to_db = [permission_0]

    for name in permissions_names:
        permission_models_to_db.append(permissions_models.Permission(name=name))

    models_to_db = user_models_to_db + permission_models_to_db
    db_session.add_all(models_to_db)
    await db_session.commit()

    user_permission_0 = permissions_models.UsersPermissions(
        permission=permission_0, user=user_0
    )
    db_session.add_all([user_permission_0])
    await db_session.commit()

    # Sign in first
    response_signin = await client.post(
        "/api/v1/auth/signin",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        content="username=superuser&password=Ab1234567!",
    )
    assert response_signin.status_code == HTTPStatus.OK

    access_token = response_signin.json()["access_token"]

    # Test api endpoint
    response = await client.get(
        "/api/v1/permissions/",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )
    assert response.status_code == HTTPStatus.OK

    data = response.json()

    assert set(data[0].keys()) == {"created_at", "modified_at", "id", "name"}
    assert len(data) == len(permission_models_to_db)


async def test_get_permission_forbidden(
    db_session: AsyncSession,
    client: AsyncClient,
) -> None:
    permission_0 = permissions_models.Permission(
        id=UUID("743a1c54-aa4c-4576-bf77-b9a0ed7d819b"),
        name="permission_read",
    )
    user_0 = users_models.User(
        id=UUID("5b90edb4-ac98-4053-ac8b-93203aa8a039"),
        username="superuser",
        password=pbkdf2_sha256.hash("Ab1234567!"),
        first_name="adam",
        last_name="smith",
    )
    permission_to_test = permissions_models.Permission(
        id=UUID("15765172-4386-4d51-b4f2-af68bb82a888"),
        name="read_movies_list",
    )
    db_session.add_all([permission_to_test, permission_0, user_0])
    await db_session.commit()

    user_permission_0 = permissions_models.UsersPermissions(
        permission=permission_to_test, user=user_0
    )
    db_session.add_all([user_permission_0])
    await db_session.commit()

    # Sign in first
    response_signin = await client.post(
        "/api/v1/auth/signin",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        content="username=superuser&password=Ab1234567!",
    )
    assert response_signin.status_code == HTTPStatus.OK

    access_token = response_signin.json()["access_token"]

    # Test api endpoint
    response = await client.get(
        "/api/v1/permissions/",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN

    data = response.json()
    assert data == {"detail": "Permission to perform this operation is not granted"}
