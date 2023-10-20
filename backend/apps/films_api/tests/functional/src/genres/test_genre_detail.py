import json
import uuid
from http import HTTPStatus
from typing import Any

import pytest
from redis import Redis
from tests.functional.conftest import ESWriteType, GetRequestType
from tests.functional.settings import Settings

pytestmark = pytest.mark.asyncio

settings = Settings.get()


@pytest.mark.parametrize(
    "genre_id, expected_status, expected_data",
    [
        (
            "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            HTTPStatus.OK,
            {"id": "3fa85f64-5717-4562-b3fc-2c963f66afa6", "name": "Action"},
        ),
    ],
)
async def test_can_get_genre_by_id(
    es_write_data: ESWriteType,
    make_get_request: GetRequestType,
    genres_access_token: str,
    genre_id: uuid.UUID,
    expected_status: int,
    expected_data: dict,
) -> None:
    es_data = [
        {
            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "name": "Action",
            "description": "Good",
        },
    ]

    await es_write_data(
        es_data,
        settings.elastic.genre_index.index,
        settings.elastic.genre_index.field_id_name,
    )
    url = f"/api/v1/genres/{genre_id}"
    body, status = await make_get_request(url, {}, genres_access_token)

    assert status == expected_status
    assert body == expected_data


@pytest.mark.parametrize(
    "genre_id, expected_status, expected_data, expected_key",
    [
        (
            "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            HTTPStatus.OK,
            {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "name": "Action",
            },
            "fastapi-cache:genre_details:a08f1196b1cfbbaaf9613d687d5fc38f",
        ),
        (
            "72b4862d-d0c8-47bc-9775-4968e59764e0",
            HTTPStatus.OK,
            {
                "id": "72b4862d-d0c8-47bc-9775-4968e59764e0",
                "name": "News",
            },
            "fastapi-cache:genre_details:66cab1f45efe21d7aaf5c6bee55a7fe0",
        ),
    ],
)
async def test_can_get_genre_by_id_from_cache(
    es_write_data: ESWriteType,
    flushable_redis_client: Redis,
    make_get_request: GetRequestType,
    genres_access_token: str,
    genre_id: uuid.UUID,
    expected_status: int,
    expected_data: dict[str, Any],
    expected_key: str,
) -> None:
    es_data = [
        {
            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "name": "Action",
            "description": "Good",
        },
        {
            "id": "72b4862d-d0c8-47bc-9775-4968e59764e0",
            "name": "News",
            "description": "Bad",
        },
    ]

    await es_write_data(
        es_data,
        settings.elastic.genre_index.index,
        settings.elastic.genre_index.field_id_name,
    )
    url = f"/api/v1/genres/{genre_id}"

    _, status = await make_get_request(url, {}, genres_access_token)
    assert status == expected_status

    raw_data = await flushable_redis_client.get(expected_key)
    assert raw_data is not None

    data = json.loads(await flushable_redis_client.get(expected_key))
    assert data == expected_data


@pytest.mark.parametrize(
    "genre_id, expected_status, expected_data",
    [
        (
            "e9c9baa8-df85-493f-a048-d2a8a642992d",
            HTTPStatus.NOT_FOUND,
            None,
        ),
    ],
)
async def test_can_get_unexistent_genre_by_id(
    make_get_request: GetRequestType,
    genres_access_token: str,
    genre_id: uuid.UUID,
    expected_status: int,
    expected_data: list[dict],
) -> None:
    url = f"/api/v1/genres/{genre_id}"
    body, status = await make_get_request(url, {}, genres_access_token)

    assert status == expected_status
    assert body == expected_data


@pytest.mark.parametrize(
    "genre_id, expected_status",
    [
        (
            "e9c9baa8-df85-493f-a048-d2a8a642992d",
            HTTPStatus.NOT_FOUND,
        ),
    ],
)
async def test_can_get_unexistent_genre_by_id_from_cache(
    flushable_redis_client: Redis,
    make_get_request: GetRequestType,
    genres_access_token: str,
    genre_id: uuid.UUID,
    expected_status: int,
) -> None:
    url = f"/api/v1/genres/{genre_id}"
    _, status = await make_get_request(url, {}, genres_access_token)

    assert status == expected_status

    cache_keys = await flushable_redis_client.keys()
    assert len(cache_keys) == 0
