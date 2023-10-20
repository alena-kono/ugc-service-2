import asyncio
from typing import Any, AsyncGenerator, Awaitable, Callable, cast
from unittest import mock

import pytest_asyncio
from httpx import AsyncClient
from redis import asyncio as aioredis
from redis.asyncio import Redis
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.common.database import Base, get_db, get_redis
from src.main import app
from src.settings.app import get_app_settings

settings = get_app_settings()

GetRequestType = Callable[
    [str, dict[str, Any]],
    Awaitable[tuple[dict, int]],
]


@pytest_asyncio.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def postgres_engine():
    engine = create_async_engine(
        settings.postgres.dsn,
        echo=settings.service.debug,
        future=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session(postgres_engine: Engine):
    async_session = cast(
        sessionmaker,
        sessionmaker(
            cast(Engine, postgres_engine),
            class_=AsyncSession,
            expire_on_commit=False,
        ),
    )

    async def override_get_db() -> AsyncGenerator[None, AsyncSession]:
        async with async_session() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db

    async with async_session() as db:
        yield db


@pytest_asyncio.fixture(scope="session", autouse=True)
async def redis_client():
    client = aioredis.from_url(
        settings.redis.dsn,
        encoding="utf-8",
        decode_responses=True,
    )

    async def override_get_redis() -> Redis:
        return client

    app.dependency_overrides[get_redis] = override_get_redis

    yield client
    await client.close()


@pytest_asyncio.fixture(scope="function")
async def flushable_redis_client(redis_client: Redis):
    async def flush():
        is_flushed = await redis_client.flushdb(asynchronous=True)
        if not is_flushed:
            raise RuntimeError("Error during flush db command to Redis")

    await flush()
    yield redis_client
    await flush()


@pytest_asyncio.fixture(scope="function")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture(scope="session", autouse=True)
async def mock_fast_api_limiter_init():
    """Mock FastAPILimiter.init() method to prevent 429 status code during tests."""
    with mock.patch(
        "fastapi_limiter.depends.FastAPILimiter", new_callable=mock.AsyncMock
    ):
        yield
