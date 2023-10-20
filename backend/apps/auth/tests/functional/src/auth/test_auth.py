from datetime import timedelta
from http import HTTPStatus
from typing import Any
from uuid import UUID

import orjson
import pytest
from httpx import AsyncClient
from passlib.hash import pbkdf2_sha256
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.auth.jwt import schemas as jwt_schemas
from src.auth.jwt.service import create_token, validate_jwt
from src.permissions import models as permissions_models
from src.settings.app import get_app_settings
from src.users import models as users_models
from src.users.settings import get_users_settings

settings = get_app_settings()
users_settings = get_users_settings()


pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "headers, content, expected_status, expected_tokens, expected_decoded_user_identity",
    [
        (
            {"Content-Type": "application/x-www-form-urlencoded"},
            "username=superuser&password=Ab1234567!",
            HTTPStatus.OK,
            {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjoiNWI5MGVkYjQtYWM5OC00MDUzLWFjOGItOTMyMDNhYThhMDM5Iiwicm9sZXMiOlsiNzQzYTFjNTQtYWE0Yy00NTc2LWJmNzctYjlhMGVkN2Q4MTliIl19LCJhY2Nlc3NfanRpIjoiMjc4ZjMzNTktN2VjNS00ZTQxLWE4MjMtODZkNWZjMDE2OTI2IiwicmVmcmVzaF9qdGkiOiJmNzUyYzRjMS1kZTZlLTRmNTQtODBkZS01Mzk2MzA2M2RmN2UiLCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjo5MTU0MDQ2NjUwLCJpYXQiOjE2ODkwODY2NTB9.dXlzNhXNWQ4rGFVfK8hXUlBVFiLZ4aNEMMh_NpbOP3U",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjoiNWI5MGVkYjQtYWM5OC00MDUzLWFjOGItOTMyMDNhYThhMDM5Iiwicm9sZXMiOlsiNzQzYTFjNTQtYWE0Yy00NTc2LWJmNzctYjlhMGVkN2Q4MTliIl19LCJhY2Nlc3NfanRpIjoiMjc4ZjMzNTktN2VjNS00ZTQxLWE4MjMtODZkNWZjMDE2OTI2IiwicmVmcmVzaF9qdGkiOiJmNzUyYzRjMS1kZTZlLTRmNTQtODBkZS01Mzk2MzA2M2RmN2UiLCJ0eXBlIjoicmVmcmVzaCIsImV4cCI6MTA2MTk4NTI2NjUwLCJpYXQiOjE2ODkwODY2NTB9.5OqhllsIGIIhn3_a8AW--3RmSQg0pqu6ohZkE35Kx7I",
            },
            {
                "user": {
                    "id": "5b90edb4-ac98-4053-ac8b-93203aa8a039",
                    "username": "superuser",
                    "first_name": "adam",
                    "last_name": "smith",
                    "permissions": ["743a1c54-aa4c-4576-bf77-b9a0ed7d819b"],
                },
            },
        ),
        (
            {"Content-Type": "application/x-www-form-urlencoded"},
            "username=regular_user&password=$ecretAb1",
            HTTPStatus.OK,
            {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjoiNGFhMDg5MzYtZjA1My00MDJkLWFkYzItYmM2M2JhOGI1MjhhIiwicm9sZXMiOlsiYjgxYjUyMWItYTNhYi00MDgyLWE5NmEtOWZmN2FlZDEyMDcxIl19LCJhY2Nlc3NfanRpIjoiM2VkZDgyYTUtZjFkMC00MGMxLThkYTEtYzQwOTg5ZjBlNWJmIiwicmVmcmVzaF9qdGkiOiI4NGQ4ZDlhNS01ODk1LTRiOTUtODU2Mi1iZGZlNWIzZjE5Y2MiLCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjo5MTU0MDQ2ODA4LCJpYXQiOjE2ODkwODY4MDh9.AELjMkF7l3oRATMSRnxpXsb5e2xhNUSSOVfrMtCBHkM",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjoiNGFhMDg5MzYtZjA1My00MDJkLWFkYzItYmM2M2JhOGI1MjhhIiwicm9sZXMiOlsiYjgxYjUyMWItYTNhYi00MDgyLWE5NmEtOWZmN2FlZDEyMDcxIl19LCJhY2Nlc3NfanRpIjoiM2VkZDgyYTUtZjFkMC00MGMxLThkYTEtYzQwOTg5ZjBlNWJmIiwicmVmcmVzaF9qdGkiOiI4NGQ4ZDlhNS01ODk1LTRiOTUtODU2Mi1iZGZlNWIzZjE5Y2MiLCJ0eXBlIjoicmVmcmVzaCIsImV4cCI6MTA2MTk4NTI2ODA4LCJpYXQiOjE2ODkwODY4MDh9.Xb7w60Ks-z8fuHstyjI81WSsV5MqACLreeoAWropD18",
            },
            {
                "user": {
                    "id": "4aa08936-f053-402d-adc2-bc63ba8b528a",
                    "username": "regular_user",
                    "first_name": "ann",
                    "last_name": "green",
                    "permissions": ["b81b521b-a3ab-4082-a96a-9ff7aed12071"],
                },
            },
        ),
    ],
)
async def test_signin_user_valid(
    db_session: AsyncSession,
    client: AsyncClient,
    headers: dict[str, str],
    content: str,
    expected_status: int,
    expected_tokens: dict[str, Any],
    expected_decoded_user_identity: dict[str, Any],
) -> None:
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

    response = await client.post(
        "/api/v1/auth/signin", headers=headers, content=content
    )
    assert response.status_code == expected_status

    data = response.json()
    assert data.keys() == expected_tokens.keys()

    access_token = await validate_jwt(token=data["access_token"])
    refresh_token = await validate_jwt(token=data["refresh_token"])

    assert access_token.type == "access"
    assert refresh_token.type == "refresh"

    assert access_token.user.id == expected_decoded_user_identity["user"]["id"]
    assert refresh_token.user.id == expected_decoded_user_identity["user"]["id"]


@pytest.mark.parametrize(
    "sign_in_events, user_agent",
    [
        (1, "firefox/1"),
        (3, "chrome/2.50"),
        (1, ""),
        (3, ""),
    ],
)
async def test_signin_user_valid_signin_is_saved(
    db_session: AsyncSession,
    client: AsyncClient,
    sign_in_events: int,
    user_agent: str,
) -> None:
    user_0 = users_models.User(
        id=UUID("5b90edb4-ac98-4053-ac8b-93203aa8a039"),
        username="superuser",
        password=pbkdf2_sha256.hash("Ab1234567!"),
        first_name="adam",
        last_name="smith",
    )
    db_session.add(user_0)
    await db_session.commit()

    for _ in range(sign_in_events):
        response = await client.post(
            "/api/v1/auth/signin",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": user_agent,
            },
            content="username=superuser&password=Ab1234567!",
        )
        assert response.status_code == HTTPStatus.OK

    stmt = select(users_models.UserSigninHistory).where(
        users_models.UserSigninHistory.user_id == user_0.id
    )
    result = await db_session.execute(stmt)
    signin_db_records = result.scalars().all()

    assert len(signin_db_records) == sign_in_events

    signin_db_record = signin_db_records[0]
    assert signin_db_record.user.id == user_0.id
    assert signin_db_record.user_agent == user_agent


@pytest.mark.parametrize(
    "sign_in_events, user_agent",
    [
        (1, "firefox/1"),
        (3, "chrome/2.50"),
        (1, ""),
        (3, ""),
    ],
)
async def test_signin_user_invalid_signin_is_not_saved(
    db_session: AsyncSession,
    client: AsyncClient,
    sign_in_events: int,
    user_agent: str,
) -> None:
    for _ in range(sign_in_events):
        response = await client.post(
            "/api/v1/auth/signin",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": user_agent,
            },
            content="username=superuser&password=Ab1234567!",
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    stmt = select(users_models.UserSigninHistory)
    result = await db_session.execute(stmt)
    signin_db_records = result.scalars().all()

    assert len(signin_db_records) == 0


@pytest.mark.parametrize(
    "headers, content, expected_status, expected_data",
    [
        (
            {"Content-Type": "application/x-www-form-urlencoded"},
            "username=fake_user&password=Ab1234567!",
            HTTPStatus.UNAUTHORIZED,
            {"detail": "Invalid user credentials"},
        ),
        (
            {"Content-Type": "application/x-www-form-urlencoded"},
            "username=superuser&password=Incorrect1!",
            HTTPStatus.UNAUTHORIZED,
            {"detail": "Invalid user credentials"},
        ),
    ],
)
async def test_signin_user_invalid(
    db_session: AsyncSession,
    client: AsyncClient,
    headers: dict[str, str],
    content: str,
    expected_status: int,
    expected_data: list[str],
) -> None:
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

    response = await client.post(
        "/api/v1/auth/signin", headers=headers, content=content
    )
    assert response.status_code == expected_status
    data = response.json()
    assert data == expected_data


@pytest.mark.parametrize(
    "headers, content, expected_status, expected_data",
    [
        (
            {"Content-Type": "application/json"},
            {
                "username": "superuser",
                "password": "Ab1234567!",
                "first_name": "adam",
                "last_name": "smith",
            },
            HTTPStatus.OK,
            {
                "username": "superuser",
                "first_name": "adam",
                "last_name": "smith",
                "permissions": [],
            },
        ),
        (
            {"Content-Type": "application/json"},
            {
                "username": "regular_user",
                "password": "$ecretAb1",
                "first_name": "ann",
                "last_name": "green",
            },
            HTTPStatus.OK,
            {
                "username": "regular_user",
                "first_name": "ann",
                "last_name": "green",
                "permissions": [],
            },
        ),
    ],
)
async def test_signup_user_does_not_exist(
    db_session: AsyncSession,
    client: AsyncClient,
    headers: dict[str, str],
    content: dict[str, str],
    expected_status: int,
    expected_data: dict[str, Any],
) -> None:
    response = await client.post(
        "/api/v1/auth/signup",
        headers=headers,
        content=orjson.dumps(content),
    )
    assert response.status_code == expected_status

    data = response.json()

    assert data is not None
    assert list(data.keys()) == [
        "id",
        "username",
        "first_name",
        "last_name",
        "permissions",
    ]
    assert data["username"] == expected_data["username"]
    assert data["first_name"] == expected_data["first_name"]
    assert data["last_name"] == expected_data["last_name"]
    assert data["permissions"] == expected_data["permissions"]

    stmt = select(users_models.User).options(
        selectinload(users_models.User.permissions)
    )
    result = await db_session.execute(stmt)
    user = result.scalar()

    assert user.username == expected_data["username"]
    assert user.first_name == expected_data["first_name"]
    assert user.last_name == expected_data["last_name"]
    assert user.permissions == expected_data["permissions"]


@pytest.mark.parametrize(
    "headers, content, expected_status, expected_data",
    [
        (
            {"Content-Type": "application/json"},
            {
                "username": "superuser",
                "password": "Ab1234567!",
                "first_name": "adam",
                "last_name": "smith",
            },
            HTTPStatus.CONFLICT,
            {"detail": "User with this username already exists"},
        ),
        (
            {"Content-Type": "application/json"},
            {
                "username": "regular_user",
                "password": "$ecretAb1",
                "first_name": "ann",
                "last_name": "green",
            },
            HTTPStatus.CONFLICT,
            {"detail": "User with this username already exists"},
        ),
    ],
)
async def test_signup_user_exists(
    db_session: AsyncSession,
    client: AsyncClient,
    headers: dict[str, str],
    content: dict[str, str],
    expected_status: int,
    expected_data: dict[str, Any],
) -> None:
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
    db_session.add_all([user_0, user_1])
    await db_session.commit()

    response = await client.post(
        "/api/v1/auth/signup",
        headers=headers,
        content=orjson.dumps(content),
    )
    assert response.status_code == expected_status

    data = response.json()

    assert data is not None
    assert data == expected_data


@pytest.mark.parametrize(
    "headers, content, expected_status, expected_data",
    [
        (
            {"Content-Type": "application/json"},
            {
                "username": "$uperuser",
                "password": "Ab1234567!",
                "first_name": "adam",
                "last_name": "smith",
            },
            HTTPStatus.UNPROCESSABLE_ENTITY,
            {
                "detail": [
                    {
                        "ctx": {"pattern": "^[a-zA-Z0-9]+(?:[ _.-][a-z0-9]+)*$"},
                        "loc": ["body", "username"],
                        "msg": 'string does not match regex "^[a-zA-Z0-9]+(?:[ _.-][a-z0-9]+)*$"',
                        "type": "value_error.str.regex",
                    }
                ]
            },
        ),
        (
            {"Content-Type": "application/json"},
            {
                "username": "regular_user",
                "password": "$ecretAb1",
                "last_name": "green",
            },
            HTTPStatus.UNPROCESSABLE_ENTITY,
            {
                "detail": [
                    {
                        "loc": ["body", "first_name"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    }
                ]
            },
        ),
    ],
)
async def test_signup_user_invalid_data(
    client: AsyncClient,
    headers: dict[str, str],
    content: dict[str, str],
    expected_status: int,
    expected_data: dict[str, Any],
) -> None:
    response = await client.post(
        "/api/v1/auth/signup",
        headers=headers,
        content=orjson.dumps(content),
    )
    assert response.status_code == expected_status

    data = response.json()

    assert data is not None
    assert data == expected_data


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
async def test_signout_user(
    db_session: AsyncSession,
    flushable_redis_client: Redis,
    client: AsyncClient,
    signin_credentials: str,
    expected_status: int,
) -> None:
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

    response = await client.post(
        "/api/v1/auth/signout",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )
    assert response.status_code == expected_status

    data = response.json()

    assert data is None

    access_jti = await flushable_redis_client.get(decoded_access_token.access_jti)
    refresh_jti = await flushable_redis_client.get(decoded_access_token.refresh_jti)

    assert access_jti is not None
    assert refresh_jti is not None


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
async def test_verify_token_valid(
    db_session: AsyncSession,
    client: AsyncClient,
    signin_credentials: str,
    expected_status: int,
) -> None:
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

    # Create fresh access token
    access_jti = "fab03b90-2ec8-47d4-8b53-386070a09dbb"
    refresh_jti = "c66cc7fb-160f-487b-9d19-090154b5a984"
    token_data = jwt_schemas.JWTIdentity(
        user=jwt_schemas.JWTUserIdentity(
            id="5b90edb4-ac98-4053-ac8b-93203aa8a039",
            permissions=["743a1c54-aa4c-4576-bf77-b9a0ed7d819b"],
        ),
        access_jti=access_jti,
        refresh_jti=refresh_jti,
    )
    access_token_to_verify = await create_token(
        data_to_encode=token_data,
        token_type="access",
        secret_key=settings.auth.jwt_secret_key,
        expires_delta=timedelta(days=1),
        algorithm=settings.auth.jwt_encoding_algorithm,
    )

    response = await client.post(
        "/api/v1/auth/token-verify",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        content=orjson.dumps({"token_string": access_token_to_verify}),
    )
    assert response.status_code == expected_status

    data = response.json()

    assert data == {
        "status": "valid",
        "detail": "Provided access token is valid",
        "provided_access_token": f"{access_token_to_verify}",
    }


@pytest.mark.parametrize(
    "signin_credentials, expected_status, access_token_to_verify, expected_data",
    [
        (
            "username=superuser&password=Ab1234567!",
            HTTPStatus.OK,
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
            {
                "status": "invalid",
                "detail": "Provided access token is invalid",
                "provided_access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
            },
        ),
        (
            "username=regular_user&password=$ecretAb1",
            HTTPStatus.OK,
            "AeyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjoiM2Q4MjVmNjAtOWZmZi00ZGZlLWIyOTQtMWE0NWZhMWUxMTVkIiwicm9sZXMiOlsiMGJiMTcxMDUtNzc3Ny00MmE3LWFmMzUtMWYyNDM5MmFjZTNkIl19LCJhY2Nlc3NfanRpIjoiYmQxYjEyMzAtOWY5NS00YzdlLWFhODQtNDZmN2E3ZWM2YWNmIiwicmVmcmVzaF9qdGkiOiI5MWMxNTY4NC01MTE5LTQ1MDQtODNlMy01ZTg3NTk0MjJlM2YiLCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjo5MTU0NDk5NjEzLCJpYXQiOjE2ODk1Mzk2MTN9.3qyhuDrM-n26_iANJk9oCkyxcZXCzI2971xWqSCmsks",
            {
                "status": "invalid",
                "detail": "Provided access token is invalid",
                "provided_access_token": "AeyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjoiM2Q4MjVmNjAtOWZmZi00ZGZlLWIyOTQtMWE0NWZhMWUxMTVkIiwicm9sZXMiOlsiMGJiMTcxMDUtNzc3Ny00MmE3LWFmMzUtMWYyNDM5MmFjZTNkIl19LCJhY2Nlc3NfanRpIjoiYmQxYjEyMzAtOWY5NS00YzdlLWFhODQtNDZmN2E3ZWM2YWNmIiwicmVmcmVzaF9qdGkiOiI5MWMxNTY4NC01MTE5LTQ1MDQtODNlMy01ZTg3NTk0MjJlM2YiLCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjo5MTU0NDk5NjEzLCJpYXQiOjE2ODk1Mzk2MTN9.3qyhuDrM-n26_iANJk9oCkyxcZXCzI2971xWqSCmsks",
            },
        ),
    ],
)
async def test_verify_token_invalid(
    db_session: AsyncSession,
    client: AsyncClient,
    signin_credentials: str,
    expected_status: int,
    access_token_to_verify: str,
    expected_data: dict[str, str],
) -> None:
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
        "/api/v1/auth/token-verify",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        content=orjson.dumps({"token_string": access_token_to_verify}),
    )
    assert response.status_code == expected_status

    data = response.json()

    assert data == expected_data


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
async def test_verify_token_invalid_revoked(
    db_session: AsyncSession,
    flushable_redis_client: Redis,
    client: AsyncClient,
    signin_credentials: str,
    expected_status: int,
) -> None:
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

    # Create fresh access token
    access_jti = "fab03b90-2ec8-47d4-8b53-386070a09dbb"
    refresh_jti = "c66cc7fb-160f-487b-9d19-090154b5a984"
    token_data = jwt_schemas.JWTIdentity(
        user=jwt_schemas.JWTUserIdentity(
            id="5b90edb4-ac98-4053-ac8b-93203aa8a039",
            permissions=["743a1c54-aa4c-4576-bf77-b9a0ed7d819b"],
        ),
        access_jti=access_jti,
        refresh_jti=refresh_jti,
    )
    access_token_to_verify = await create_token(
        data_to_encode=token_data,
        token_type="access",
        secret_key=settings.auth.jwt_secret_key,
        expires_delta=timedelta(days=1),
        algorithm=settings.auth.jwt_encoding_algorithm,
    )

    # Put tokens' jtis into a storage containing revoked tokens
    await flushable_redis_client.set(name=access_jti, value="")
    await flushable_redis_client.set(name=refresh_jti, value="")

    response = await client.post(
        "/api/v1/auth/token-verify",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        content=orjson.dumps({"token_string": access_token_to_verify}),
    )
    assert response.status_code == expected_status

    data = response.json()

    assert data == {
        "status": "invalid",
        "detail": "Provided access token is invalid",
        "provided_access_token": f"{access_token_to_verify}",
    }


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
async def test_refresh_token_valid(
    db_session: AsyncSession,
    client: AsyncClient,
    signin_credentials: str,
    expected_status: int,
) -> None:
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
    refresh_token = response_signin.json()["refresh_token"]

    response = await client.post(
        "/api/v1/auth/token-refresh",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        content=orjson.dumps({"token_string": refresh_token}),
    )
    assert response.status_code == expected_status

    data = response.json()

    assert data is not None
    assert data["access_token"] is not None
    assert data["refresh_token"] is not None


@pytest.mark.parametrize(
    "signin_credentials, expected_status",
    [
        (
            "username=superuser&password=Ab1234567!",
            HTTPStatus.CONFLICT,
        ),
        (
            "username=regular_user&password=$ecretAb1",
            HTTPStatus.CONFLICT,
        ),
    ],
)
async def test_refresh_token_invalid_from_another_user(
    db_session: AsyncSession,
    client: AsyncClient,
    signin_credentials: str,
    expected_status: int,
) -> None:
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

    # Create refresh token with another user identity
    access_jti = "fab03b90-2ec8-47d4-8b53-386070a09dbb"
    refresh_jti = "c66cc7fb-160f-487b-9d19-090154b5a984"
    token_data = jwt_schemas.JWTIdentity(
        user=jwt_schemas.JWTUserIdentity(
            id="4f94e19f-f9a3-4b53-b925-016cefc615c7",
            permissions=[],
        ),
        access_jti=access_jti,
        refresh_jti=refresh_jti,
    )
    refresh_token = await create_token(
        data_to_encode=token_data,
        token_type="refresh",
        secret_key=settings.auth.jwt_secret_key,
        expires_delta=timedelta(days=1),
        algorithm=settings.auth.jwt_encoding_algorithm,
    )

    response = await client.post(
        "/api/v1/auth/token-refresh",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        content=orjson.dumps({"token_string": refresh_token}),
    )
    assert response.status_code == expected_status

    data = response.json()

    assert data is not None
    assert data == {"detail": "Invalid refresh token"}
