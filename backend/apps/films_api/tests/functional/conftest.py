import asyncio
import json
import time
from collections import defaultdict
from http import HTTPStatus
from pathlib import Path
from typing import Any, Awaitable, Callable
from uuid import uuid4

import aiohttp
import pytest
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from jose import jwt as jose_jwt
from redis import Redis
from redis import asyncio as aioredis
from src.common.schemas import JwtClaims, JwtUserSchema
from tests.functional.settings import Settings

BASE_PATH = Path(__file__).parent

settings = Settings.get()

GetRequestType = Callable[
    [str, dict[str, Any], str | None],
    Awaitable[tuple[dict, int]],
]
ESWriteType = Callable[
    [list[dict], str, str],
    Awaitable[None],
]
TokenGeneratorType = Callable[[list[str]], str]


@pytest_asyncio.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def es_client():
    async def create_index_if_not_exist(
        client: AsyncElasticsearch, filename: str, index: str
    ):
        file_path = BASE_PATH / f"testdata/{filename}.json"

        with open(file_path, "r") as schema_config:
            config = json.load(schema_config)
            await client.indices.create(index=index, body=config, ignore=400)

    client = AsyncElasticsearch(settings.elastic.dsn)
    for filename, index in [
        ("es_genres_schema", settings.elastic.genre_index.index),
        ("es_movies_schema", settings.elastic.film_index.index),
        ("es_persons_schema", settings.elastic.person_index.index),
    ]:
        await create_index_if_not_exist(client, filename, index)

    yield client

    await client.indices.delete(settings.elastic.genre_index.index)
    await client.indices.delete(settings.elastic.film_index.index)
    await client.indices.delete(settings.elastic.person_index.index)
    await client.close()


@pytest_asyncio.fixture(scope="session")
async def service_session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


def get_es_bulk_query(data: list[dict], index: str, id_field: str):
    bulk_query = []
    for row in data:
        bulk_query.extend(
            [
                json.dumps(
                    {
                        "index": {
                            "_index": index,
                            "_id": row[id_field],
                        }
                    }
                ),
                json.dumps(row),
            ]
        )
    return bulk_query


@pytest_asyncio.fixture
async def es_write_data(es_client: AsyncElasticsearch):
    data_written = defaultdict(lambda: set())

    async def write_data_inner(data: list[dict], index: str, id_field: str):
        data_written[index].update({i[id_field] for i in data})

        bulk_query = get_es_bulk_query(data, index, id_field)
        str_query = "\n".join(bulk_query) + "\n"

        response = await es_client.bulk(str_query, refresh=True)
        if response["errors"]:
            raise RuntimeError("Error during write to Elasticsearch")

    async def delete_index_inner():
        for index, docs in data_written.items():
            for doc_id in docs:
                await es_client.delete(index=index, id=doc_id)

    yield write_data_inner
    await delete_index_inner()


@pytest_asyncio.fixture(scope="session")
async def redis_client():
    client = aioredis.from_url(
        settings.redis.dsn,
        encoding="utf-8",
        decode_responses=True,
    )
    yield client
    await client.close()


@pytest_asyncio.fixture(scope="function")
async def flushable_redis_client(redis_client: Redis):
    async def flush():
        is_flushed = await redis_client.flushdb(asynchronous=True)
        if not is_flushed:
            raise RuntimeError("Error during flushdb command to Redis")

    await flush()
    yield redis_client
    await flush()


@pytest.fixture
def make_get_request(service_session: aiohttp.ClientSession):
    async def inner(
        path: str, query_data: dict[str, Any], access_token: str | None = None
    ) -> tuple[dict | None, int]:
        url = f"{settings.backend.url}{path}"

        async with service_session.get(
            url,
            params=query_data,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
        ) as response:
            status = response.status
            body = await response.json() if status == HTTPStatus.OK else None

        return body, status

    return inner


@pytest.fixture
def token_generator() -> Callable[[list[str]], str]:
    def _token_generator(permissions: list[str]) -> str:
        time_now = time.time()
        time_delta = 10
        token_claims = JwtClaims(
            user=JwtUserSchema(id=str(uuid4()), permissions=permissions),
            type="access",
            exp=time_now + time_delta,
            iat=time_now,
            access_jti=str(uuid4()),
            refresh_jti=str(uuid4()),
        )
        return jose_jwt.encode(
            claims=token_claims.dict(),
            key=settings.auth.jwt_secret_key,
            algorithm=settings.auth.jwt_encoding_algorithm,
        )

    return _token_generator


@pytest.fixture(scope="function")
def films_access_token(token_generator: TokenGeneratorType) -> str:
    return token_generator(["can_read_films"])


@pytest.fixture(scope="function")
def genres_access_token(token_generator: TokenGeneratorType) -> str:
    return token_generator(["can_read_genres"])


@pytest.fixture(scope="function")
def persons_access_token(token_generator: TokenGeneratorType) -> str:
    return token_generator(["can_read_persons"])
