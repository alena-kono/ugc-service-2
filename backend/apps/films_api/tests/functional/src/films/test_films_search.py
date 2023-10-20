import json
import uuid
from http import HTTPStatus

import pytest
from redis import Redis
from tests.functional.conftest import ESWriteType, GetRequestType
from tests.functional.settings import Settings

pytestmark = pytest.mark.asyncio

settings = Settings.get()
FILMS_URL = "/api/v1/films/search"


@pytest.mark.parametrize(
    "query_data, expected_status, expected_length",
    [
        (
            {
                "page_size": 10,
                "page_number": 1,
                "sort_by": "imdb_rating",
                "order_by": "desc",
            },
            HTTPStatus.OK,
            10,
        ),
        (
            {
                "query": "test empty query",
                "page_size": 10,
            },
            HTTPStatus.OK,
            0,
        ),
    ],
)
async def test_films_search(
    es_write_data: ESWriteType,
    make_get_request: GetRequestType,
    films_access_token: str,
    query_data: dict[str, str],
    expected_status: int,
    expected_length: int,
) -> None:
    film_index = settings.elastic.film_index.index
    id_field = settings.elastic.film_index.field_id_name
    es_data = [
        {
            "id": str(uuid.uuid4()),
            "imdb_rating": 8.5,
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
        }
        for _ in range(60)
    ]
    await es_write_data(es_data, film_index, id_field)

    body, status = await make_get_request(
        "/api/v1/films/search", query_data, films_access_token
    )

    assert status == expected_status
    assert len(body) == expected_length


@pytest.mark.parametrize(
    "query_data, expected_status, expected_data, expected_key",
    [
        (
            {
                "query": "Star",
                "page_size": 2,
                "page_number": 1,
                "sort_by": "imdb_rating",
                "order_by": "desc",
            },
            HTTPStatus.OK,
            [
                {
                    "id": "29271693-942d-4698-b7a5-9ac0f504f90c",
                    "imdb_rating": 9,
                    "title": "The Star",
                },
                {
                    "id": "e9c9baa8-df85-493f-a048-d2a8a642992d",
                    "imdb_rating": 7,
                    "title": "North Star",
                },
            ],
            "fastapi-cache:films_search:676140a4bf996c84f7630d676565bff4",
        ),
        (
            {
                "query": "test empty query",
                "page_size": 10,
                "page_number": 1,
            },
            HTTPStatus.OK,
            [],
            "fastapi-cache:films_search:98be41ab8871283acce3ae662a6404c4",
        ),
    ],
)
async def test_films_search_from_cache(
    es_write_data: ESWriteType,
    flushable_redis_client: Redis,
    make_get_request: GetRequestType,
    films_access_token: str,
    query_data: dict[str, str],
    expected_status: int,
    expected_key: str,
    expected_data: list[dict],
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
            "directors": [],
            "actors": [],
            "writers": [],
        },
        {
            "id": "e9c9baa8-df85-493f-a048-d2a8a642992d",
            "imdb_rating": 7,
            "genres": [
                {"id": "32780457-805a-45fe-8916-2de3461f48e7", "name": "Sci-Fi"},
            ],
            "title": "North Star",
            "description": "The coldest one",
            "directors_names": [],
            "actors_names": [],
            "writers_names": [],
            "directors": [],
            "actors": [],
            "writers": [],
        },
    ] * 20

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
    "query_data, expected_status, expected_length",
    [
        ({"page_size": 1, "page_number": 1}, HTTPStatus.OK, 1),
        ({"page_size": 1, "page_number": 2}, HTTPStatus.OK, 1),
    ],
)
async def test_films_search_can_paginate(
    es_write_data: ESWriteType,
    make_get_request: GetRequestType,
    films_access_token: str,
    query_data: dict[str, str],
    expected_status: int,
    expected_length: int,
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
    assert len(body) == expected_length

    page_number = int(query_data["page_number"]) - 1
    assert es_data[page_number]["id"] == body[0]["id"]


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
async def test_films_search_can_sort(
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
async def test_films_search_can_filter(
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
async def test_films_search_can_handle_wrong_args(
    make_get_request: GetRequestType,
    films_access_token: str,
    query_data: dict[str, str],
    expected_status: int,
) -> None:
    _, status = await make_get_request(FILMS_URL, query_data, films_access_token)

    assert status == expected_status
