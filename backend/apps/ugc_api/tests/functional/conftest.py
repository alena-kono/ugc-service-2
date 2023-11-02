import asyncio
from time import time
from typing import Any, Awaitable, Callable
from unittest import mock
from uuid import uuid4

import pytest_asyncio
from aiokafka import AIOKafkaProducer
from httpx import AsyncClient
from motor.core import AgnosticClient
from motor.motor_asyncio import AsyncIOMotorClient
from src.common.authorization import JwtClaims, JwtUserSchema
from src.common.databases import get_kafka_producer, get_mongodb
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
async def db_session():
    mongodb = AsyncIOMotorClient(settings.mongo.dsn)
    producer = mock.AsyncMock()

    def get_test_mongodb() -> AgnosticClient:
        if mongodb is None:
            raise RuntimeError("MongoDB client has not been defined.")

        return mongodb

    def get_test_kafka_producer() -> AIOKafkaProducer:
        if producer is None:
            raise RuntimeError("Kafka producer has not been defined.")

        return producer

    app.dependency_overrides[get_mongodb] = get_test_mongodb
    app.dependency_overrides[get_kafka_producer] = get_test_kafka_producer

    yield mongodb

    collections = await mongodb[settings.mongo.db_name].list_collection_names()
    for collection in collections:
        await mongodb[settings.mongo.db_name].drop_collection(collection)


@pytest_asyncio.fixture(scope="function")
async def client():
    base_url = f"http://{settings.service.host}:{settings.service.port}/api/v1"
    async with AsyncClient(app=app, base_url=base_url) as client:
        yield client


@pytest_asyncio.fixture(scope="session", autouse=True)
async def mock_fast_api_limiter_init():
    """Mock FastAPILimiter.init() method to prevent 429 status code during tests."""
    with mock.patch(
        "fastapi_limiter.depends.FastAPILimiter", new_callable=mock.AsyncMock
    ):
        yield


@pytest_asyncio.fixture(scope="session", autouse=True)
async def mock_jwt():
    jwt_user = JwtUserSchema(
        id=str(uuid4()),
        permissions=["test"],
    )
    jwt_claim = JwtClaims(
        user=jwt_user,
        iat=1,
        access_jti="test",
        refresh_jti="test",
        type="test",
        exp=int(time()) + 60,
    )

    with mock.patch("src.common.authorization.decode_token") as mock_jwt:
        mock_jwt.return_value = jwt_claim
        yield jwt_claim
