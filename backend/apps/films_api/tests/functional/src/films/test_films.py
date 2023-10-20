import json
import uuid
from http import HTTPStatus

import pytest
from redis import Redis
from tests.functional.conftest import ESWriteType, GetRequestType
from tests.functional.settings import Settings

pytestmark = pytest.mark.asyncio

settings = Settings.get()
FILMS_URL = "/api/v1/films/"


@pytest.mark.parametrize(
    "query_data, expected_status, expected_data",
    [
        (
            {"page_size": 1, "page_number": 1},
            HTTPStatus.OK,
            [
                {
                    "id": "72b4862d-d0c8-47bc-9775-4968e59764e0",
                    "imdb_rating": 9,
                    "title": "The Star",
                }
            ],
        ),
        (
            {"page_size": 1, "page_number": 2},
            HTTPStatus.OK,
            [
                {
                    "id": "e9c9baa8-df85-493f-a048-d2a8a642992d",
                    "imdb_rating": 8.5,
                    "title": "Harry Potter",
                }
            ],
        ),
    ],
)
async def test_films_can_paginate(
    es_write_data: ESWriteType,
    make_get_request: GetRequestType,
    films_access_token: str,
    query_data: dict[str, str],
    expected_status: int,
    expected_data: list[dict],
) -> None:
    es_data = [
        {
            "id": "72b4862d-d0c8-47bc-9775-4968e59764e0",
            "imdb_rating": 9,
            "genres": [
                {"id": str(uuid.uuid4()), "name": "Action"},
                {"id": str(uuid.uuid4()), "name": "Sci-fi"},
            ],
            "title": "The Star",
            "description": "New World",
            "directors_names": ["Stan"],
            "actors_names": ["Ann", "Bob"],
            "writers_names": ["Ben", "Howard"],
            "directors": [
                {"id": str(uuid.uuid4()), "full_name": "Rob"},
                {"id": str(uuid.uuid4()), "full_name": "Zorg"},
            ],
            "actors": [
                {"id": str(uuid.uuid4()), "full_name": "Ann"},
                {"id": str(uuid.uuid4()), "full_name": "Bob"},
            ],
            "writers": [
                {"id": str(uuid.uuid4()), "full_name": "Ben"},
                {"id": str(uuid.uuid4()), "full_name": "Howard"},
            ],
        },
        {
            "id": "e9c9baa8-df85-493f-a048-d2a8a642992d",
            "imdb_rating": 8.5,
            "genres": [
                {"id": str(uuid.uuid4()), "name": "Action"},
                {"id": str(uuid.uuid4()), "name": "Sci-fi"},
            ],
            "title": "Harry Potter",
            "description": "magic",
            "directors_names": ["John"],
            "actors_names": ["Ann", "Bob"],
            "writers_names": ["Ben", "Howard"],
            "directors": [
                {"id": str(uuid.uuid4()), "full_name": "Rob"},
                {"id": str(uuid.uuid4()), "full_name": "Zorg"},
            ],
            "actors": [
                {"id": str(uuid.uuid4()), "full_name": "Ann"},
                {"id": str(uuid.uuid4()), "full_name": "Bob"},
            ],
            "writers": [
                {"id": str(uuid.uuid4()), "full_name": "Ben"},
                {"id": str(uuid.uuid4()), "full_name": "Howard"},
            ],
        },
    ]

    await es_write_data(
        es_data,
        settings.elastic.film_index.index,
        settings.elastic.film_index.field_id_name,
    )
    body, status = await make_get_request(FILMS_URL, query_data, films_access_token)

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
                {
                    "id": "e9c9baa8-df85-493f-a048-d2a8a642992d",
                    "imdb_rating": 9,
                    "title": "The Star",
                },
                {
                    "id": "72b4862d-d0c8-47bc-9775-4968e59764e0",
                    "imdb_rating": 7,
                    "title": "Harry Potter",
                },
            ],
            "fastapi-cache:films:e88797e652dde95728534511e590d4a8",
        ),
        (
            {"page_size": 1, "page_number": 2},
            HTTPStatus.OK,
            [
                {
                    "id": "72b4862d-d0c8-47bc-9775-4968e59764e0",
                    "imdb_rating": 7,
                    "title": "Harry Potter",
                },
            ],
            "fastapi-cache:films:21851e4e5e4dfe2f0015b6d0171fad10",
        ),
    ],
)
async def test_get_films_from_cache(
    es_write_data: ESWriteType,
    flushable_redis_client: Redis,
    make_get_request: GetRequestType,
    films_access_token: str,
    query_data: dict[str, str],
    expected_status: int,
    expected_data: list[dict],
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
    ] * 2

    await es_write_data(
        es_data,
        settings.elastic.film_index.index,
        settings.elastic.film_index.field_id_name,
    )

    _, status = await make_get_request(FILMS_URL, query_data, films_access_token)
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
            {"page_size": 2, "sort_by": "imdb_rating", "order_by": "desc"},
            HTTPStatus.OK,
        ),
        (
            {"page_size": 2, "sort_by": "imdb_rating", "order_by": "asc"},
            HTTPStatus.OK,
        ),
    ],
)
async def test_films_sort(
    es_write_data: ESWriteType,
    make_get_request: GetRequestType,
    films_access_token: str,
    query_data: dict[str, str],
    expected_status: int,
) -> None:
    es_data = [
        {
            "id": str(uuid.uuid4()),
            "imdb_rating": 9,
            "genres": [
                {"id": str(uuid.uuid4()), "name": "Action"},
                {"id": str(uuid.uuid4()), "name": "Sci-fi"},
            ],
            "title": "The Star",
            "description": "New World",
            "directors_names": ["Stan"],
            "actors_names": ["Ann", "Bob"],
            "writers_names": ["Ben", "Howard"],
            "directors": [
                {"id": str(uuid.uuid4()), "full_name": "Rob"},
                {"id": str(uuid.uuid4()), "full_name": "Zorg"},
            ],
            "actors": [
                {"id": str(uuid.uuid4()), "full_name": "Ann"},
                {"id": str(uuid.uuid4()), "full_name": "Bob"},
            ],
            "writers": [
                {"id": str(uuid.uuid4()), "full_name": "Ben"},
                {"id": str(uuid.uuid4()), "full_name": "Howard"},
            ],
        },
        {
            "id": str(uuid.uuid4()),
            "imdb_rating": 8,
            "genres": [
                {"id": str(uuid.uuid4()), "name": "Action"},
                {"id": str(uuid.uuid4()), "name": "Sci-fi"},
            ],
            "title": "Harry Potter",
            "description": "magic",
            "directors_names": ["John"],
            "actors_names": ["Ann", "Bob"],
            "writers_names": ["Ben", "Howard"],
            "directors": [
                {"id": str(uuid.uuid4()), "full_name": "Rob"},
                {"id": str(uuid.uuid4()), "full_name": "Zorg"},
            ],
            "actors": [
                {"id": str(uuid.uuid4()), "full_name": "Ann"},
                {"id": str(uuid.uuid4()), "full_name": "Bob"},
            ],
            "writers": [
                {"id": str(uuid.uuid4()), "full_name": "Ben"},
                {"id": str(uuid.uuid4()), "full_name": "Howard"},
            ],
        },
    ]

    await es_write_data(
        es_data,
        settings.elastic.film_index.index,
        settings.elastic.film_index.field_id_name,
    )
    body, status = await make_get_request(FILMS_URL, query_data, films_access_token)

    assert status == expected_status
    assert len(body) == 2

    if query_data["order_by"] == "asc":
        assert es_data[1]["id"] == body[0]["id"]
    else:
        assert es_data[0]["id"] == body[0]["id"]


@pytest.mark.parametrize(
    "query_data, expected_status, expected_length, expected_id",
    [
        (
            {
                "page_size": 2,
                "filter_by": "genre_id",
                "filter_value": "63d4cbaa-79e7-4ee8-a215-1f87a8829e53",
            },
            HTTPStatus.OK,
            1,
            "29271693-942d-4698-b7a5-9ac0f504f90c",
        ),
        (
            {
                "page_size": 2,
                "filter_by": "genre_id",
                "filter_value": "be119190-cfa8-44c8-ac49-e7e4d20e4671",
            },
            HTTPStatus.OK,
            1,
            "103f7583-db4c-4c4c-8980-32051276dd4e",
        ),
    ],
)
async def test_films_filter(
    es_write_data: ESWriteType,
    make_get_request: GetRequestType,
    films_access_token: str,
    query_data: dict[str, str],
    expected_status: int,
    expected_length: int,
    expected_id: uuid.UUID,
) -> None:
    es_data = [
        {
            "id": "29271693-942d-4698-b7a5-9ac0f504f90c",
            "imdb_rating": 9,
            "genres": [
                {"id": "63d4cbaa-79e7-4ee8-a215-1f87a8829e53", "name": "Action"},
            ],
            "title": "The Star",
            "description": "New World",
            "directors_names": ["Stan"],
            "actors_names": ["Ann", "Bob"],
            "writers_names": ["Ben", "Howard"],
            "directors": [
                {"id": str(uuid.uuid4()), "full_name": "Rob"},
            ],
            "actors": [
                {"id": str(uuid.uuid4()), "full_name": "Ann"},
            ],
            "writers": [
                {"id": str(uuid.uuid4()), "full_name": "Ben"},
            ],
        },
        {
            "id": "103f7583-db4c-4c4c-8980-32051276dd4e",
            "imdb_rating": 8,
            "genres": [
                {"id": "be119190-cfa8-44c8-ac49-e7e4d20e4671", "name": "Horror"},
            ],
            "title": "Harry Potter",
            "description": "magic",
            "directors_names": ["John"],
            "actors_names": ["Ann", "Bob"],
            "writers_names": ["Ben", "Howard"],
            "directors": [
                {"id": str(uuid.uuid4()), "full_name": "Rob"},
            ],
            "actors": [
                {"id": str(uuid.uuid4()), "full_name": "Ann"},
            ],
            "writers": [
                {"id": str(uuid.uuid4()), "full_name": "Ben"},
            ],
        },
    ]

    await es_write_data(
        es_data,
        settings.elastic.film_index.index,
        settings.elastic.film_index.field_id_name,
    )
    body, status = await make_get_request(FILMS_URL, query_data, films_access_token)

    assert status == expected_status
    assert len(body) == expected_length
    assert body[0]["id"] == expected_id


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
        ({"filter_by": "e"}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"filter_by": 0}, HTTPStatus.UNPROCESSABLE_ENTITY),
    ],
)
async def test_films_can_handle_wrong_args(
    make_get_request: GetRequestType,
    films_access_token: str,
    query_data: dict[str, str],
    expected_status: int,
) -> None:
    _, status = await make_get_request(FILMS_URL, query_data, films_access_token)

    assert status == expected_status
