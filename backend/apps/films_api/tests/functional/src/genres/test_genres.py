import json
from http import HTTPStatus

import pytest
from redis import Redis
from tests.functional.conftest import ESWriteType, GetRequestType
from tests.functional.settings import Settings

pytestmark = pytest.mark.asyncio

settings = Settings.get()
GENRES_URL = "/api/v1/genres/"


@pytest.mark.parametrize(
    "query_data, expected_status, expected_data",
    [
        (
            {"page_size": 10, "page_number": 1},
            HTTPStatus.OK,
            [
                {"id": "32780457-805a-45fe-8916-2de3461f48e7", "name": "8"},
                {"id": "72b4862d-d0c8-47bc-9775-4968e59764e0", "name": "Action"},
            ],
        ),
    ],
)
async def test_get_genres(
    es_write_data: ESWriteType,
    make_get_request: GetRequestType,
    genres_access_token: str,
    query_data: dict[str, str],
    expected_status: int,
    expected_data: list[dict],
) -> None:
    es_data = [
        {
            "id": "72b4862d-d0c8-47bc-9775-4968e59764e0",
            "name": "Action",
            "description": None,
        },
        {
            "id": "32780457-805a-45fe-8916-2de3461f48e7",
            "name": 8,
        },
    ]

    await es_write_data(
        es_data,
        settings.elastic.genre_index.index,
        settings.elastic.genre_index.field_id_name,
    )

    body, status = await make_get_request(GENRES_URL, query_data, genres_access_token)

    assert status == expected_status
    assert len(body) == len(expected_data)
    assert body == expected_data


@pytest.mark.parametrize(
    "query_data, expected_status, expected_data",
    [
        (
            {"page_size": 1, "page_number": 1},
            HTTPStatus.OK,
            [
                {
                    "id": "72b4862d-d0c8-47bc-9775-4968e59764e0",
                    "name": "Action",
                },
            ],
        ),
        (
            {"page_size": 1, "page_number": 2},
            HTTPStatus.OK,
            [
                {
                    "id": "e9c9baa8-df85-493f-a048-d2a8a642992d",
                    "name": "News",
                },
            ],
        ),
    ],
)
async def test_genres_can_paginate(
    es_write_data: ESWriteType,
    make_get_request: GetRequestType,
    genres_access_token: str,
    query_data: dict[str, str],
    expected_status: int,
    expected_data: list[dict],
) -> None:
    es_data = [
        {
            "id": "72b4862d-d0c8-47bc-9775-4968e59764e0",
            "name": "Action",
        },
        {
            "id": "e9c9baa8-df85-493f-a048-d2a8a642992d",
            "name": "News",
        },
    ]

    await es_write_data(
        es_data,
        settings.elastic.genre_index.index,
        settings.elastic.genre_index.field_id_name,
    )
    body, status = await make_get_request(GENRES_URL, query_data, genres_access_token)

    assert status == expected_status
    assert len(body) == len(expected_data)
    assert body == expected_data

    page_number = int(query_data["page_number"]) - 1
    assert es_data[page_number]["id"] == body[0]["id"]


@pytest.mark.parametrize(
    "query_data, expected_status, expected_data, expected_key",
    [
        (
            {"page_size": 10, "page_number": 1},
            HTTPStatus.OK,
            [
                {"id": "32780457-805a-45fe-8916-2de3461f48e7", "name": "Action"},
                {"id": "f491d132-abd0-40f5-aff5-75d894741f5f", "name": "News"},
            ],
            "fastapi-cache:genres:5ec85a57d4628cc425e426bc77fe55f8",
        ),
        (
            {"page_size": 1, "page_number": 2},
            HTTPStatus.OK,
            [
                {"id": "f491d132-abd0-40f5-aff5-75d894741f5f", "name": "News"},
            ],
            "fastapi-cache:genres:d0fcb839d838bee066bdba99aa78f699",
        ),
    ],
)
async def test_get_genres_from_cache(
    es_write_data: ESWriteType,
    flushable_redis_client: Redis,
    make_get_request: GetRequestType,
    genres_access_token: str,
    query_data: dict[str, str],
    expected_status: int,
    expected_data: list[dict],
    expected_key: str,
) -> None:
    es_data = [
        {
            "id": "32780457-805a-45fe-8916-2de3461f48e7",
            "name": "Action",
            "description": "Good",
        },
        {
            "id": "f491d132-abd0-40f5-aff5-75d894741f5f",
            "name": "News",
            "description": "Bad",
        },
    ]

    await es_write_data(
        es_data,
        settings.elastic.genre_index.index,
        settings.elastic.genre_index.field_id_name,
    )

    _, status = await make_get_request(GENRES_URL, query_data, genres_access_token)

    assert status == expected_status

    raw_data = await flushable_redis_client.get(expected_key)
    assert raw_data is not None

    data = json.loads(await flushable_redis_client.get(expected_key))
    assert len(data) == len(expected_data)
    assert data == expected_data


@pytest.mark.parametrize(
    "query_data, expected_status",
    [
        (
            {"page_size": 2, "sort_by": "name", "order_by": "desc"},
            HTTPStatus.OK,
        ),
        (
            {"page_size": 2, "sort_by": "name", "order_by": "asc"},
            HTTPStatus.OK,
        ),
    ],
)
async def test_genres_sort(
    es_write_data: ESWriteType,
    make_get_request: GetRequestType,
    genres_access_token: str,
    query_data: dict[str, str],
    expected_status: int,
) -> None:
    es_data = [
        {
            "id": "f491d132-abd0-40f5-aff5-75d894741f5f",
            "name": "News",
            "description": "Bad",
        },
        {
            "id": "32780457-805a-45fe-8916-2de3461f48e7",
            "name": "Action",
            "description": "Good",
        },
    ]

    await es_write_data(
        es_data,
        settings.elastic.genre_index.index,
        settings.elastic.genre_index.field_id_name,
    )
    body, status = await make_get_request(GENRES_URL, query_data, genres_access_token)

    assert status == expected_status
    assert len(body) == len(es_data)

    if query_data["order_by"] == "asc":
        assert es_data[1]["id"] == body[0]["id"]
    else:
        assert es_data[0]["id"] == body[0]["id"]


@pytest.mark.parametrize(
    "query_data, expected_status",
    [
        ({"page_number": 0}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"page_number": -1}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"page_number": "e"}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"page_size": 0}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"page_size": "e"}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"page_size": -1}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"sort_by": "e"}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"sort_by": 0}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"order_by": "e"}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"order_by": 0}, HTTPStatus.UNPROCESSABLE_ENTITY),
    ],
)
async def test_genres_can_handle_wrong_args(
    make_get_request: GetRequestType,
    genres_access_token: str,
    query_data: dict[str, str],
    expected_status: int,
) -> None:
    _, status = await make_get_request(GENRES_URL, query_data, genres_access_token)

    assert status == expected_status
