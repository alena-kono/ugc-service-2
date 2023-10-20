import pytest
from passlib.hash import pbkdf2_sha256
from sqlalchemy import exc as sqlalchemy_exc
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.permissions import models as permissions_models
from src.permissions.enums import ServiceInternalPermission
from src.users import models as users_models
from src.users.repositories import PostgresUserRepository

pytestmark = pytest.mark.asyncio


async def test_get_user(
    db_session: AsyncSession,
) -> None:
    test_permission = permissions_models.Permission(
        name=ServiceInternalPermission.permission_delete
    )
    test_permission2 = permissions_models.Permission(
        name=ServiceInternalPermission.permission_update
    )
    user_model = users_models.User(
        username="test_name",
        password="123qwe",
        first_name="test",
        last_name="test",
    )
    db_session.add_all([test_permission, test_permission2, user_model])
    await db_session.commit()

    user_permission = permissions_models.UsersPermissions(
        permission=test_permission, user=user_model
    )
    user_permission2 = permissions_models.UsersPermissions(
        permission=test_permission2, user=user_model
    )
    db_session.add_all([user_permission, user_permission2])
    await db_session.commit()

    repo = PostgresUserRepository(db_session)
    user = await repo.get(user_model.id)

    assert user is not None
    assert user.id == user_model.id
    assert user.username == user_model.username
    assert user.first_name == user_model.first_name
    assert user.last_name == user_model.last_name
    expected_permissions = [test_permission2.name, test_permission.name]
    assert set(user.permissions) == set(expected_permissions)


@pytest.mark.parametrize(
    "filter_kwargs, expected_results_len",
    [
        ({"username": "test_name"}, 1),
        ({"first_name": "adam"}, 2),
        ({"username": "fake"}, 0),
        ({"username": "fake", "first_name": "adam"}, 0),
    ],
)
async def test_filter_by_user(
    db_session: AsyncSession,
    filter_kwargs: dict[str, str],
    expected_results_len: int,
) -> None:
    user_0 = users_models.User(
        username="test_name",
        password="123qwe",
        first_name="adam",
        last_name="smith",
    )
    user_1 = users_models.User(
        username="common_name",
        password="secret",
        first_name="adam",
        last_name="johnson",
    )
    db_session.add_all([user_0, user_1])
    await db_session.commit()

    repo = PostgresUserRepository(db_session)
    users = await repo.filter_by(**filter_kwargs)

    assert users is not None
    assert isinstance(users, list)
    assert len(users) == expected_results_len


async def test_create_user(
    db_session: AsyncSession,
) -> None:
    user_data = {
        "username": "superuser",
        "password": "Ab1234567!",
        "first_name": "adam",
        "last_name": "smith",
    }
    repo = PostgresUserRepository(db_session)
    created_user_0 = await repo.create(
        username=user_data["username"],
        password=user_data["password"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
    )
    stmt = select(users_models.User).options(
        selectinload(users_models.User.permissions)
    )
    result = await db_session.execute(stmt)
    user_db = result.scalar()

    assert created_user_0 is not None
    assert user_db is not None
    assert created_user_0.id == user_db.id
    assert created_user_0.username == user_db.username
    assert created_user_0.first_name == user_db.first_name
    assert created_user_0.last_name == user_db.last_name


async def test_create_user_same_username_disallowed(
    db_session: AsyncSession,
) -> None:
    user_data_0 = {
        "username": "superuser",
        "password": "Ab1234567!",
        "first_name": "adam",
        "last_name": "smith",
    }
    user_data_1 = {
        "username": "superuser",
        "password": "$ecretAb1",
        "first_name": "ann",
        "last_name": "green",
    }
    repo = PostgresUserRepository(db_session)
    await repo.create(**user_data_0)

    with pytest.raises(sqlalchemy_exc.IntegrityError):
        await repo.create(**user_data_1)


@pytest.mark.parametrize(
    "user_data_0, user_data_1",
    [
        (
            {
                "username": "superuser",
                "password": "Ab1234567!",
                "first_name": "adam",
                "last_name": "smith",
            },
            {
                "username": "regular_user",
                "password": "Ab1234567!",
                "first_name": "adam",
                "last_name": "smith",
            },
        ),
        (
            {
                "username": "superuser",
                "password": "Ab1234567!",
                "first_name": "adam",
                "last_name": "smith",
            },
            {
                "username": "regular_user",
                "password": "Ab1234567!",
                "first_name": "ann",
                "last_name": "green",
            },
        ),
        (
            {
                "username": "superuser",
                "password": "Ab1234567!",
                "first_name": "adam",
                "last_name": "smith",
            },
            {
                "username": "regular_user",
                "password": "Ab1234567!",
                "first_name": "adam",
                "last_name": "green",
            },
        ),
        (
            {
                "username": "superuser",
                "password": "Ab1234567!",
                "first_name": "adam",
                "last_name": "smith",
            },
            {
                "username": "regular_user",
                "password": "Ab1234567!",
                "first_name": "ann",
                "last_name": "smith",
            },
        ),
    ],
)
async def test_create_user_same_fields_allowed(
    db_session: AsyncSession,
    user_data_0: dict[str, str],
    user_data_1: dict[str, str],
) -> None:
    repo = PostgresUserRepository(db_session)
    created_user_0 = await repo.create(**user_data_0)
    created_user_1 = await repo.create(**user_data_1)

    stmt = (
        select(users_models.User)
        .options(selectinload(users_models.User.permissions))
        .order_by(users_models.User.created_at.asc())
    )
    result = await db_session.execute(stmt)
    users_db = result.scalars().all()

    assert len(users_db) == 2

    assert created_user_0.id == users_db[0].id
    assert created_user_0.username == users_db[0].username
    assert created_user_0.first_name == users_db[0].first_name
    assert created_user_0.last_name == users_db[0].last_name

    assert created_user_1.id == users_db[1].id
    assert created_user_1.username == users_db[1].username
    assert created_user_1.first_name == users_db[1].first_name
    assert created_user_1.last_name == users_db[1].last_name


async def test_update_user(
    db_session: AsyncSession,
) -> None:
    expected_name = "test_name"

    user_model = users_models.User(
        username="original_name",
        password="123qwe",
        first_name="test",
        last_name="test",
    )
    db_session.add(user_model)
    await db_session.commit()

    repo = PostgresUserRepository(db_session)
    user = await repo.update(user_model.id, username=expected_name)

    assert user is not None
    assert user.id == user_model.id
    assert user.username == expected_name
    assert user.first_name == user_model.first_name
    assert user.last_name == user_model.last_name


async def test_check_password(
    db_session: AsyncSession,
) -> None:
    test_password = "test_password"
    wrong_password = "wrong_password"

    user_model = users_models.User(
        username="original_name",
        password=pbkdf2_sha256.hash(test_password),
        first_name="test",
        last_name="test",
    )
    db_session.add(user_model)
    await db_session.commit()

    repo = PostgresUserRepository(db_session)

    assert True is await repo.check_password(user_model.id, password=test_password)
    assert False is await repo.check_password(user_model.id, password=wrong_password)


async def test_change_password(
    db_session: AsyncSession,
) -> None:
    new_password = "new_password"

    user_model = users_models.User(
        username="original_name",
        password=pbkdf2_sha256.hash("original"),
        first_name="test",
        last_name="test",
    )
    db_session.add(user_model)
    await db_session.commit()

    repo = PostgresUserRepository(db_session)
    await repo.change_password(user_model.id, new_password=new_password)
    assert True is await repo.check_password(user_model.id, password=new_password)


async def test_assign_permission(
    db_session: AsyncSession,
) -> None:
    permission = permissions_models.Permission(
        name=ServiceInternalPermission.user_delete
    )
    user = users_models.User(
        username="original_name",
        password=pbkdf2_sha256.hash("original"),
        first_name="test",
        last_name="test",
    )
    db_session.add_all([user, permission])
    await db_session.commit()

    repo = PostgresUserRepository(db_session)
    await repo.assign_permission(user_id=user.id, permission_id=permission.id)
    user_schema = await repo.get(user_id=user.id)

    assert user_schema.permissions[0] == permission.name
