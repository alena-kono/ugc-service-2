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
    "film_id, expected_status, expected_data",
    [
        (
            "e9c9baa8-df85-493f-a048-d2a8a642992d",
            HTTPStatus.OK,
            {
                "id": "e9c9baa8-df85-493f-a048-d2a8a642992d",
                "imdb_rating": 9,
                "genres": [
                    {"id": "63d4cbaa-79e7-4ee8-a215-1f87a8829e53", "name": "Action"},
                ],
                "title": "The Star",
                "description": "New World",
                "directors": [],
                "actors": [],
                "writers": [],
            },
        ),
    ],
)
async def test_can_get_film_by_id(
    es_write_data: ESWriteType,
    make_get_request: GetRequestType,
    films_access_token: str,
    film_id: uuid.UUID,
    expected_status: int,
    expected_data: dict,
) -> None:
    es_data = [
        {
            "id": "e9c9baa8-df85-493f-a048-d2a8a642992d",
            "imdb_rating": 9,
            "genres": [
                {"id": "63d4cbaa-79e7-4ee8-a215-1f87a8829e53", "name": "Action"},
            ],
            "title": "The Star",
            "description": "New World",
            "directors_names": ["Stan"],
            "actors_names": ["Ann", "Bob"],
            "writers_names": ["Ben", "Howard"],
            "directors": [],
            "actors": [],
            "writers": [],
        },
    ]

    await es_write_data(
        es_data,
        settings.elastic.film_index.index,
        settings.elastic.film_index.field_id_name,
    )
    url = f"/api/v1/films/{film_id}"
    body, status = await make_get_request(url, {}, films_access_token)

    assert status == expected_status
    assert body == expected_data


@pytest.mark.parametrize(
    "film_id, expected_status, expected_data, expected_key",
    [
        (
            "e9c9baa8-df85-493f-a048-d2a8a642992d",
            HTTPStatus.OK,
            {
                "id": "e9c9baa8-df85-493f-a048-d2a8a642992d",
                "imdb_rating": 9,
                "genres": [
                    {"id": "63d4cbaa-79e7-4ee8-a215-1f87a8829e53", "name": "Action"},
                ],
                "title": "The Star",
                "description": "New World",
                "directors": [],
                "actors": [],
                "writers": [],
            },
            "fastapi-cache:film_details:d818e2dc99af84130a5197b8bae19898",
        ),
        (
            "72b4862d-d0c8-47bc-9775-4968e59764e0",
            HTTPStatus.OK,
            {
                "id": "72b4862d-d0c8-47bc-9775-4968e59764e0",
                "imdb_rating": 7,
                "genres": [
                    {"id": "f491d132-abd0-40f5-aff5-75d894741f5f", "name": "Sci-Fi"},
                ],
                "title": "Harry Potter",
                "description": "magic",
                "directors": [
                    {"id": "35030d14-cd8e-4b14-899c-7bf6939f4863", "full_name": "Rob"},
                ],
                "actors": [
                    {"id": "7f63bfd2-18d6-4ec1-87b6-8fc8b99968a8", "full_name": "Ann"},
                    {"id": "654958ff-9ea6-45f6-b8eb-986c30ce0b2c", "full_name": "Bob"},
                ],
                "writers": [
                    {"id": "35030d14-cd8e-4b14-899c-7bf6939f4863", "full_name": "Ben"},
                ],
            },
            "fastapi-cache:film_details:c5c729b534e17f80d0a07c6390876bd7",
        ),
    ],
)
async def test_can_get_film_by_id_from_cache(
    es_write_data: ESWriteType,
    flushable_redis_client: Redis,
    make_get_request: GetRequestType,
    films_access_token: str,
    film_id: uuid.UUID,
    expected_status: int,
    expected_data: dict[str, Any],
    expected_key: str,
) -> None:
    es_data = [
        {
            "id": "e9c9baa8-df85-493f-a048-d2a8a642992d",
            "imdb_rating": 9,
            "genres": [
                {"id": "63d4cbaa-79e7-4ee8-a215-1f87a8829e53", "name": "Action"},
            ],
            "title": "The Star",
            "description": "New World",
            "directors_names": ["Stan"],
            "actors_names": ["Ann", "Bob"],
            "writers_names": ["Ben", "Howard"],
            "directors": [],
            "actors": [],
            "writers": [],
        },
        {
            "id": "72b4862d-d0c8-47bc-9775-4968e59764e0",
            "imdb_rating": 7,
            "genres": [
                {"id": "f491d132-abd0-40f5-aff5-75d894741f5f", "name": "Sci-Fi"},
            ],
            "title": "Harry Potter",
            "description": "magic",
            "directors_names": ["Rob"],
            "actors_names": ["Ann", "Bob"],
            "writers_names": ["Ben"],
            "directors": [
                {"id": "35030d14-cd8e-4b14-899c-7bf6939f4863", "full_name": "Rob"},
            ],
            "actors": [
                {"id": "7f63bfd2-18d6-4ec1-87b6-8fc8b99968a8", "full_name": "Ann"},
                {"id": "654958ff-9ea6-45f6-b8eb-986c30ce0b2c", "full_name": "Bob"},
            ],
            "writers": [
                {"id": "35030d14-cd8e-4b14-899c-7bf6939f4863", "full_name": "Ben"},
            ],
        },
    ]

    await es_write_data(
        es_data,
        settings.elastic.film_index.index,
        settings.elastic.film_index.field_id_name,
    )
    url = f"/api/v1/films/{film_id}"

    _, status = await make_get_request(url, {}, films_access_token)
    assert status == expected_status

    raw_data = await flushable_redis_client.get(expected_key)
    assert raw_data is not None

    data = json.loads(await flushable_redis_client.get(expected_key))
    assert data == expected_data


@pytest.mark.parametrize(
    "film_id, expected_status",
    [
        (
            "e9c9baa8-df85-493f-a048-d2a8a642992d",
            HTTPStatus.NOT_FOUND,
        ),
    ],
)
async def test_can_get_unexistent_film_by_id(
    make_get_request: GetRequestType,
    films_access_token: str,
    film_id: uuid.UUID,
    expected_status: int,
) -> None:
    url = f"/api/v1/films/{film_id}"
    _, status = await make_get_request(url, {}, films_access_token)

    assert status == expected_status


@pytest.mark.parametrize(
    "film_id, expected_status, expected_data, expected_key",
    [
        (
            "e9c9baa8-df85-493f-a048-d2a8a642992d",
            HTTPStatus.NOT_FOUND,
            None,
            "",
        ),
    ],
)
async def test_can_get_unexistent_film_by_id_from_cache(
    flushable_redis_client: Redis,
    make_get_request: GetRequestType,
    films_access_token: str,
    film_id: uuid.UUID,
    expected_status: int,
    expected_data: dict[str, Any],
    expected_key: str,
) -> None:
    url = f"/api/v1/films/{film_id}"
    _, status = await make_get_request(url, {}, films_access_token)

    assert status == expected_status

    raw_data = await flushable_redis_client.get(expected_key)
    assert raw_data == expected_data

    cache_keys = await flushable_redis_client.keys()
    cache_key = ""
    if len(cache_keys) == 1:
        cache_key = cache_keys[0]
    assert cache_key == expected_key
