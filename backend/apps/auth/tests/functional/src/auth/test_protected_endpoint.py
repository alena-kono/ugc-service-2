from http import HTTPStatus
from uuid import UUID

import pytest
from httpx import AsyncClient
from passlib.hash import pbkdf2_sha256
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.jwt.service import validate_jwt
from src.permissions import models as permissions_models
from src.users import models as users_models

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "signin_credentials, expected_status",
    [
        (
            "username=superuser&password=Ab1234567!",
            HTTPStatus.OK,
        ),
        (
            "username=regular_user&password=$ecretAb1",
            HTTPStatus.OK,
        ),
    ],
)
async def test_protected_endpoint_valid_token(
    db_session: AsyncSession,
    client: AsyncClient,
    signin_credentials: str,
    expected_status: int,
) -> None:
    """Test an API endpoint protected by JWT authorization."""
    permission_0 = permissions_models.Permission(
        id=UUID("743a1c54-aa4c-4576-bf77-b9a0ed7d819b"),
        name="admin",
    )
    permission_1 = permissions_models.Permission(
        id=UUID("b81b521b-a3ab-4082-a96a-9ff7aed12071"),
        name="subscriber",
    )
    user_0 = users_models.User(
        id=UUID("5b90edb4-ac98-4053-ac8b-93203aa8a039"),
        username="superuser",
        password=pbkdf2_sha256.hash("Ab1234567!"),
        first_name="adam",
        last_name="smith",
    )
    user_1 = users_models.User(
        id=UUID("4aa08936-f053-402d-adc2-bc63ba8b528a"),
        username="regular_user",
        password=pbkdf2_sha256.hash("$ecretAb1"),
        first_name="ann",
        last_name="green",
    )
    db_session.add_all([permission_0, permission_1, user_0, user_1])
    await db_session.commit()

    user_permission_0 = permissions_models.UsersPermissions(
        permission=permission_0, user=user_0
    )
    user_permission_1 = permissions_models.UsersPermissions(
        permission=permission_1, user=user_1
    )
    db_session.add_all([user_permission_0, user_permission_1])
    await db_session.commit()

    # Sign in first to get an access token
    response_signin = await client.post(
        "/api/v1/auth/signin",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        content=signin_credentials,
    )
    access_token = response_signin.json()["access_token"]

    response = await client.post(
        "/api/v1/auth/signout",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "signin_credentials, expected_status, expected_data",
    [
        (
            "username=superuser&password=Ab1234567!",
            HTTPStatus.UNAUTHORIZED,
            {"detail": "Invalid access token"},
        ),
        (
            "username=regular_user&password=$ecretAb1",
            HTTPStatus.UNAUTHORIZED,
            {"detail": "Invalid access token"},
        ),
    ],
)
async def test_protected_endpoint_invalid_token(
    db_session: AsyncSession,
    client: AsyncClient,
    signin_credentials: str,
    expected_status: int,
    expected_data: dict[str, str],
) -> None:
    """Test an API endpoint protected by JWT authorization."""
    permission_0 = permissions_models.Permission(
        id=UUID("743a1c54-aa4c-4576-bf77-b9a0ed7d819b"),
        name="admin",
    )
    permission_1 = permissions_models.Permission(
        id=UUID("b81b521b-a3ab-4082-a96a-9ff7aed12071"),
        name="subscriber",
    )
    user_0 = users_models.User(
        id=UUID("5b90edb4-ac98-4053-ac8b-93203aa8a039"),
        username="superuser",
        password=pbkdf2_sha256.hash("Ab1234567!"),
        first_name="adam",
        last_name="smith",
    )
    user_1 = users_models.User(
        id=UUID("4aa08936-f053-402d-adc2-bc63ba8b528a"),
        username="regular_user",
        password=pbkdf2_sha256.hash("$ecretAb1"),
        first_name="ann",
        last_name="green",
    )
    db_session.add_all([permission_0, permission_1, user_0, user_1])
    await db_session.commit()

    user_permission_0 = permissions_models.UsersPermissions(
        permission=permission_0, user=user_0
    )
    user_permission_1 = permissions_models.UsersPermissions(
        permission=permission_1, user=user_1
    )
    db_session.add_all([user_permission_0, user_permission_1])
    await db_session.commit()

    # Sign in first to get an access token
    response_signin = await client.post(
        "/api/v1/auth/signin",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        content=signin_credentials,
    )
    access_token = response_signin.json()["access_token"]
    corrupted_access_token = access_token + "bad"

    response = await client.post(
        "/api/v1/auth/signout",
        headers={
            "Authorization": f"Bearer {corrupted_access_token}",
            "Content-Type": "application/json",
        },
    )
    assert response.status_code == expected_status

    data = response.json()

    assert data == expected_data


@pytest.mark.parametrize(
    "signin_credentials, expected_status, expected_data",
    [
        (
            "username=superuser&password=Ab1234567!",
            HTTPStatus.UNAUTHORIZED,
            {"detail": "Invalid access token"},
        ),
        (
            "username=regular_user&password=$ecretAb1",
            HTTPStatus.UNAUTHORIZED,
            {"detail": "Invalid access token"},
        ),
    ],
)
async def test_protected_endpoint_revoked_token(
    db_session: AsyncSession,
    flushable_redis_client: Redis,
    client: AsyncClient,
    signin_credentials: str,
    expected_status: int,
    expected_data: dict[str, str],
) -> None:
    """Test an API endpoint protected by JWT authorization."""
    permission_0 = permissions_models.Permission(
        id=UUID("743a1c54-aa4c-4576-bf77-b9a0ed7d819b"),
        name="admin",
    )
    permission_1 = permissions_models.Permission(
        id=UUID("b81b521b-a3ab-4082-a96a-9ff7aed12071"),
        name="subscriber",
    )
    user_0 = users_models.User(
        id=UUID("5b90edb4-ac98-4053-ac8b-93203aa8a039"),
        username="superuser",
        password=pbkdf2_sha256.hash("Ab1234567!"),
        first_name="adam",
        last_name="smith",
    )
    user_1 = users_models.User(
        id=UUID("4aa08936-f053-402d-adc2-bc63ba8b528a"),
        username="regular_user",
        password=pbkdf2_sha256.hash("$ecretAb1"),
        first_name="ann",
        last_name="green",
    )
    db_session.add_all([permission_0, permission_1, user_0, user_1])
    await db_session.commit()

    user_permission_0 = permissions_models.UsersPermissions(
        permission=permission_0, user=user_0
    )
    user_permission_1 = permissions_models.UsersPermissions(
        permission=permission_1, user=user_1
    )
    db_session.add_all([user_permission_0, user_permission_1])
    await db_session.commit()

    # Sign in first to get an access token
    response_signin = await client.post(
        "/api/v1/auth/signin",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        content=signin_credentials,
    )
    access_token = response_signin.json()["access_token"]
    decoded_access_token = await validate_jwt(access_token)

    # Put tokens into a storage containing revoked tokens
    await flushable_redis_client.set(name=decoded_access_token.access_jti, value="")
    await flushable_redis_client.set(name=decoded_access_token.refresh_jti, value="")

    response = await client.post(
        "/api/v1/auth/signout",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )
    assert response.status_code == expected_status

    data = response.json()

    assert data == expected_data
