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
PERSONS_URL = "/api/v1/persons/"


@pytest.mark.parametrize(
    "query_data, expected_status, expected_length",
    [
        ({"page_size": 1, "page_number": 1}, HTTPStatus.OK, 1),
        ({"page_size": 1, "page_number": 2}, HTTPStatus.OK, 1),
    ],
)
async def test_persons_can_paginate(
    es_write_data: ESWriteType,
    make_get_request: GetRequestType,
    persons_access_token: str,
    query_data: dict[str, str],
    expected_status: int,
    expected_length: int,
) -> None:
    es_data = [
        {"id": str(uuid.uuid4()), "full_name": "Alena"},
        {"id": str(uuid.uuid4()), "full_name": "Pavel"},
    ]

    await es_write_data(
        es_data,
        settings.elastic.person_index.index,
        settings.elastic.person_index.field_id_name,
    )
    body, status = await make_get_request(PERSONS_URL, query_data, persons_access_token)

    assert status == expected_status
    assert len(body) == expected_length

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
                    "full_name": "Alena",
                    "films": [
                        {
                            "id": "abc9baa8-df85-493f-a048-d2a8a642992d",
                            "roles": ["actor"],
                        }
                    ],
                },
                {
                    "id": "72b4862d-d0c8-47bc-9775-4968e59764e0",
                    "full_name": "Pavel",
                    "films": [
                        {
                            "id": "cdc9baa8-df85-493f-a048-d2a8a642992d",
                            "roles": ["writer"],
                        }
                    ],
                },
            ],
            "fastapi-cache:persons:9f1a26290ee1c77c6117aa0c2049205b",
        )
    ],
)
async def test_get_persons_from_cache(
    es_write_data: ESWriteType,
    flushable_redis_client: Redis,
    make_get_request: GetRequestType,
    persons_access_token: str,
    query_data: dict[str, str],
    expected_status: int,
    expected_data: list[dict],
    expected_key: str,
) -> None:
    persons_es_data = [
        {"id": "e9c9baa8-df85-493f-a048-d2a8a642992d", "full_name": "Alena"},
        {"id": "72b4862d-d0c8-47bc-9775-4968e59764e0", "full_name": "Pavel"},
    ]

    movies_es_data = [
        {
            "id": "abc9baa8-df85-493f-a048-d2a8a642992d",
            "imdb_rating": 9,
            "genres": [
                {"id": "63d4cbaa-79e7-4ee8-a215-1f87a8829e53", "name": "Action"},
            ],
            "title": "The Star",
            "description": "New World",
            "directors_names": [],
            "actors_names": ["Alena"],
            "writers_names": [],
            "directors": [],
            "actors": [
                {"id": "e9c9baa8-df85-493f-a048-d2a8a642992d", "full_name": "Alena"},
            ],
            "writers": [],
        },
        {
            "id": "cdc9baa8-df85-493f-a048-d2a8a642992d",
            "imdb_rating": 8,
            "genres": [
                {"id": "63d4cbaa-79e7-4ee8-a215-1f87a8829e53", "name": "Action"},
            ],
            "title": "Harry Potter",
            "description": "magic",
            "directors_names": [],
            "actors_names": [],
            "writers_names": ["Pavel"],
            "directors": [],
            "actors": [],
            "writers": [
                {"id": "72b4862d-d0c8-47bc-9775-4968e59764e0", "full_name": "Pavel"},
            ],
        },
    ]

    await es_write_data(
        persons_es_data,
        settings.elastic.person_index.index,
        settings.elastic.person_index.field_id_name,
    )

    await es_write_data(
        movies_es_data,
        settings.elastic.film_index.index,
        settings.elastic.film_index.field_id_name,
    )

    _, status = await make_get_request(PERSONS_URL, query_data, persons_access_token)

    assert status == expected_status

    raw_data = await flushable_redis_client.get(expected_key)
    assert json.loads(raw_data) == expected_data


@pytest.mark.parametrize(
    "query_data, expected_status, expected_data",
    [
        (
            {
                "page_size": 2,
                "page_number": 1,
                "sort_by": "full_name",
                "order_by": "asc",
            },
            HTTPStatus.OK,
            [
                {
                    "id": "e9c9baa8-df85-493f-a048-d2a8a642992d",
                    "full_name": "Alena",
                    "films": [
                        {
                            "id": "abc9baa8-df85-493f-a048-d2a8a642992d",
                            "roles": ["actor"],
                        }
                    ],
                },
                {
                    "id": "72b4862d-d0c8-47bc-9775-4968e59764e0",
                    "full_name": "Pavel",
                    "films": [
                        {
                            "id": "cdc9baa8-df85-493f-a048-d2a8a642992d",
                            "roles": ["writer"],
                        }
                    ],
                },
            ],
        ),
        (
            {
                "page_size": 2,
                "page_number": 1,
                "sort_by": "full_name",
                "order_by": "desc",
            },
            HTTPStatus.OK,
            [
                {
                    "id": "72b4862d-d0c8-47bc-9775-4968e59764e0",
                    "full_name": "Pavel",
                    "films": [
                        {
                            "id": "cdc9baa8-df85-493f-a048-d2a8a642992d",
                            "roles": ["writer"],
                        }
                    ],
                },
                {
                    "id": "e9c9baa8-df85-493f-a048-d2a8a642992d",
                    "full_name": "Alena",
                    "films": [
                        {
                            "id": "abc9baa8-df85-493f-a048-d2a8a642992d",
                            "roles": ["actor"],
                        }
                    ],
                },
            ],
        ),
    ],
)
async def test_persons_sort(
    es_write_data: ESWriteType,
    make_get_request: GetRequestType,
    persons_access_token: str,
    query_data: dict[str, str],
    expected_status: int,
    expected_data: list[dict],
) -> None:
    persons_es_data = [
        {"id": "e9c9baa8-df85-493f-a048-d2a8a642992d", "full_name": "Alena"},
        {"id": "72b4862d-d0c8-47bc-9775-4968e59764e0", "full_name": "Pavel"},
    ]

    movies_es_data = [
        {
            "id": "abc9baa8-df85-493f-a048-d2a8a642992d",
            "imdb_rating": 9,
            "genres": [
                {"id": "63d4cbaa-79e7-4ee8-a215-1f87a8829e53", "name": "Action"},
            ],
            "title": "The Star",
            "description": "New World",
            "directors_names": [],
            "actors_names": ["Alena"],
            "writers_names": [],
            "directors": [],
            "actors": [
                {"id": "e9c9baa8-df85-493f-a048-d2a8a642992d", "full_name": "Alena"},
            ],
            "writers": [],
        },
        {
            "id": "cdc9baa8-df85-493f-a048-d2a8a642992d",
            "imdb_rating": 8,
            "genres": [
                {"id": "63d4cbaa-79e7-4ee8-a215-1f87a8829e53", "name": "Action"},
            ],
            "title": "Harry Potter",
            "description": "magic",
            "directors_names": [],
            "actors_names": [],
            "writers_names": ["Pavel"],
            "directors": [],
            "actors": [],
            "writers": [
                {"id": "72b4862d-d0c8-47bc-9775-4968e59764e0", "full_name": "Pavel"},
            ],
        },
    ]

    await es_write_data(
        persons_es_data,
        settings.elastic.person_index.index,
        settings.elastic.person_index.field_id_name,
    )

    await es_write_data(
        movies_es_data,
        settings.elastic.film_index.index,
        settings.elastic.film_index.field_id_name,
    )

    body, status = await make_get_request(PERSONS_URL, query_data, persons_access_token)

    assert status == expected_status
    assert body == expected_data


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
async def test_persons_can_handle_wrong_args(
    make_get_request: GetRequestType,
    persons_access_token: str,
    query_data: dict[str, Any],
    expected_status: int,
) -> None:
    _, status = await make_get_request(PERSONS_URL, query_data, persons_access_token)

    assert status == expected_status
