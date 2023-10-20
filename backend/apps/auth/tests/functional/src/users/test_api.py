from http import HTTPStatus
from uuid import UUID

import orjson
import pytest
from httpx import AsyncClient
from passlib.hash import pbkdf2_sha256
from sqlalchemy.ext.asyncio import AsyncSession
from src.permissions import models as permissions_models
from src.users import models as users_models

pytestmark = pytest.mark.asyncio


async def test_get_user_by_id(db_session: AsyncSession, client: AsyncClient) -> None:
    permission = permissions_models.Permission(
        id=UUID("743a1c54-aa4c-4576-bf77-b9a0ed7d819b"),
        name="user_read",
    )
    user = users_models.User(
        id=UUID("5b90edb4-ac98-4053-ac8b-93203aa8a039"),
        username="superuser",
        password=pbkdf2_sha256.hash("Ab1234567!"),
        first_name="adam",
        last_name="smith",
    )
    db_session.add_all([permission, user])
    await db_session.commit()

    user_permission = permissions_models.UsersPermissions(
        permission=permission, user=user
    )
    db_session.add_all([user_permission])
    await db_session.commit()

    response_signin = await client.post(
        "/api/v1/auth/signin",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        content="username=superuser&password=Ab1234567!",
    )
    access_token = response_signin.json()["access_token"]

    response_user = await client.get(
        "/api/v1/users/5b90edb4-ac98-4053-ac8b-93203aa8a039",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    data = response_user.json()

    assert response_user.status_code == HTTPStatus.OK
    assert data == {
        "id": "5b90edb4-ac98-4053-ac8b-93203aa8a039",
        "username": "superuser",
        "first_name": "adam",
        "last_name": "smith",
        "permissions": ["user_read"],
    }

    response_not_found = await client.get(
        "/api/v1/users/5b90edb4-ac98-4053-ac8b-93203aa8a030",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response_not_found.status_code == HTTPStatus.NOT_FOUND


async def test_get_user_history(db_session: AsyncSession, client: AsyncClient) -> None:
    permission = permissions_models.Permission(
        id=UUID("743a1c54-aa4c-4576-bf77-b9a0ed7d819b"),
        name="user_read",
    )
    user = users_models.User(
        id=UUID("5b90edb4-ac98-4053-ac8b-93203aa8a039"),
        username="superuser",
        password=pbkdf2_sha256.hash("Ab1234567!"),
        first_name="adam",
        last_name="smith",
    )
    db_session.add_all([permission, user])
    await db_session.commit()

    user_permission = permissions_models.UsersPermissions(
        permission=permission, user=user
    )
    db_session.add_all([user_permission])
    await db_session.commit()

    response_signin = await client.post(
        "/api/v1/auth/signin",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        content="username=superuser&password=Ab1234567!",
    )
    access_token = response_signin.json()["access_token"]

    response_user_history = await client.get(
        "/api/v1/users/5b90edb4-ac98-4053-ac8b-93203aa8a039/signin-history",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    data = response_user_history.json()

    assert response_user_history.status_code == HTTPStatus.OK
    assert len(data["items"]) == 1
    assert "user_agent" in data["items"][0]
    assert data["items"][0]["ip_address"] == "127.0.0.1"

    response_history_not_exist = await client.get(
        "/api/v1/users/5b90edb4-ac98-4053-ac8b-93203aa8a030/signin-history",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response_history_not_exist.status_code == HTTPStatus.NOT_FOUND


async def test_change_password(db_session: AsyncSession, client: AsyncClient) -> None:
    permission = permissions_models.Permission(
        id=UUID("743a1c54-aa4c-4576-bf77-b9a0ed7d819b"),
        name="user_update",
    )
    user = users_models.User(
        id=UUID("5b90edb4-ac98-4053-ac8b-93203aa8a039"),
        username="superuser",
        password=pbkdf2_sha256.hash("Ab1234567"),
        first_name="adam",
        last_name="smith",
    )
    db_session.add_all([permission, user])
    await db_session.commit()

    user_permission = permissions_models.UsersPermissions(
        permission=permission, user=user
    )
    db_session.add_all([user_permission])
    await db_session.commit()

    response_signin = await client.post(
        "/api/v1/auth/signin",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        content="username=superuser&password=Ab1234567",
    )
    access_token = response_signin.json()["access_token"]

    response_successful_password_change = await client.post(
        "/api/v1/users/5b90edb4-ac98-4053-ac8b-93203aa8a039/password-change",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        content=orjson.dumps({"old_password": "Ab1234567", "password": "Ab12345678"}),
    )

    assert response_successful_password_change.status_code == HTTPStatus.OK

    response_invalid_cred_password_change = await client.post(
        "/api/v1/users/5b90edb4-ac98-4053-ac8b-93203aa8a039/password-change",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        content=orjson.dumps({"old_password": "Ab1234567", "password": "Ab12345678"}),
    )

    assert response_invalid_cred_password_change.status_code == HTTPStatus.UNAUTHORIZED

    response_user_not_exist_password_change = await client.post(
        "/api/v1/users/5b90edb4-ac98-4053-ac8b-93203aa8a030/password-change",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        content=orjson.dumps({"old_password": "Ab1234567", "password": "Ab12345678"}),
    )

    assert response_user_not_exist_password_change.status_code == HTTPStatus.NOT_FOUND


async def test_assign_permission(db_session: AsyncSession, client: AsyncClient) -> None:
    permission_update = permissions_models.Permission(
        id=UUID("743a1c54-aa4c-4576-bf77-b9a0ed7d819b"),
        name="user_update",
    )
    permission_read = permissions_models.Permission(
        id=UUID("743a1c54-aa4c-4576-bf77-b9a0ed7d819a"),
        name="user_read",
    )
    user = users_models.User(
        id=UUID("5b90edb4-ac98-4053-ac8b-93203aa8a039"),
        username="superuser",
        password=pbkdf2_sha256.hash("Ab1234567"),
        first_name="adam",
        last_name="smith",
    )
    db_session.add_all([permission_update, permission_read, user])
    await db_session.commit()

    user_permission = permissions_models.UsersPermissions(
        permission=permission_update, user=user
    )
    db_session.add_all([user_permission])
    await db_session.commit()

    response_signin = await client.post(
        "/api/v1/auth/signin",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        content="username=superuser&password=Ab1234567",
    )
    access_token = response_signin.json()["access_token"]

    response_assign_permissions = await client.post(
        "/api/v1/users/5b90edb4-ac98-4053-ac8b-93203aa8a039/assign-permission",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        content=orjson.dumps(
            {
                "permission_id": "743a1c54-aa4c-4576-bf77-b9a0ed7d819a",
            }
        ),
    )
    user_data = response_assign_permissions.json()

    assert response_assign_permissions.status_code == HTTPStatus.OK
    assert user_data["permissions"] == [
        "user_update",
        "user_read",
    ]

    response_permission_not_exist = await client.post(
        "/api/v1/users/5b90edb4-ac98-4053-ac8b-93203aa8a039/assign-permission",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        content=orjson.dumps(
            {
                "permission_id": "743a1c54-aa4c-4576-bf77-b9a0ed7d819c",
            }
        ),
    )

    assert response_permission_not_exist.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    response_assign_permission_user_not_exist = await client.post(
        "/api/v1/users/5b90edb4-ac98-4053-ac8b-93203aa8a038/assign-permission",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        content=orjson.dumps(
            {
                "permission_id": "743a1c54-aa4c-4576-bf77-b9a0ed7d819b",
            }
        ),
    )

    assert response_assign_permission_user_not_exist.status_code == HTTPStatus.NOT_FOUND


async def test_revoke_permission(db_session: AsyncSession, client: AsyncClient) -> None:
    permission_update = permissions_models.Permission(
        id=UUID("743a1c54-aa4c-4576-bf77-b9a0ed7d819b"),
        name="user_update",
    )
    permission_read = permissions_models.Permission(
        id=UUID("743a1c54-aa4c-4576-bf77-b9a0ed7d819a"),
        name="user_read",
    )
    user = users_models.User(
        id=UUID("5b90edb4-ac98-4053-ac8b-93203aa8a039"),
        username="superuser",
        password=pbkdf2_sha256.hash("Ab1234567"),
        first_name="adam",
        last_name="smith",
    )
    db_session.add_all([permission_update, permission_read, user])
    await db_session.commit()

    user_permission_update = permissions_models.UsersPermissions(
        permission=permission_update, user=user
    )
    user_permission_read = permissions_models.UsersPermissions(
        permission=permission_read, user=user
    )
    db_session.add_all([user_permission_update, user_permission_read])
    await db_session.commit()

    response_signin = await client.post(
        "/api/v1/auth/signin",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        content="username=superuser&password=Ab1234567",
    )
    access_token = response_signin.json()["access_token"]

    response_revoke_permissions = await client.post(
        "/api/v1/users/5b90edb4-ac98-4053-ac8b-93203aa8a039/revoke-permission",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        content=orjson.dumps(
            {
                "permission_id": "743a1c54-aa4c-4576-bf77-b9a0ed7d819a",
            }
        ),
    )
    user_data = response_revoke_permissions.json()

    assert response_revoke_permissions.status_code == HTTPStatus.OK
    assert user_data["permissions"] == ["user_update"]

    response_revoke_permission_user_not_exist = await client.post(
        "/api/v1/users/6b90edb4-ac98-4053-ac8b-93203aa8a039/revoke-permission",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        content=orjson.dumps(
            {
                "permission_id": "743a1c54-aa4c-4576-bf77-b9a0ed7d819a",
            }
        ),
    )

    assert response_revoke_permission_user_not_exist.status_code == HTTPStatus.NOT_FOUND


async def test_update_user(db_session: AsyncSession, client: AsyncClient) -> None:
    permission_update = permissions_models.Permission(
        id=UUID("743a1c54-aa4c-4576-bf77-b9a0ed7d819b"),
        name="user_update",
    )
    user = users_models.User(
        id=UUID("5b90edb4-ac98-4053-ac8b-93203aa8a039"),
        username="superuser",
        password=pbkdf2_sha256.hash("Ab1234567"),
        first_name="adam",
        last_name="smith",
    )
    db_session.add_all([permission_update, user])
    await db_session.commit()

    user_permission_update = permissions_models.UsersPermissions(
        permission=permission_update, user=user
    )
    db_session.add_all([user_permission_update])
    await db_session.commit()

    response_signin = await client.post(
        "/api/v1/auth/signin",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        content="username=superuser&password=Ab1234567",
    )
    access_token = response_signin.json()["access_token"]

    response_update_user = await client.put(
        "/api/v1/users/5b90edb4-ac98-4053-ac8b-93203aa8a039",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        content=orjson.dumps(
            {"username": "superuser2", "first_name": "adam2", "last_name": "smith2"}
        ),
    )
    user_data = response_update_user.json()

    assert response_update_user.status_code == HTTPStatus.OK
    assert user_data["username"] == "superuser2"
    assert user_data["first_name"] == "adam2"
    assert user_data["last_name"] == "smith2"

    response_update_user_not_exist = await client.put(
        "/api/v1/users/7b90edb4-ac98-4053-ac8b-93203aa8a039",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        content=orjson.dumps(
            {"username": "superuser2", "first_name": "adam2", "last_name": "smith2"}
        ),
    )

    assert response_update_user_not_exist.status_code == HTTPStatus.NOT_FOUND
