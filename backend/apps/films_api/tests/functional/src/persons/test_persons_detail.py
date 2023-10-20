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
PERSONS_URL = "/api/v1/persons"


@pytest.mark.parametrize(
    "person_id, expected_status, expected_data",
    [
        (
            "72b4862d-d0c8-47bc-9775-4968e59764e0",
            HTTPStatus.OK,
            {
                "id": "72b4862d-d0c8-47bc-9775-4968e59764e0",
                "full_name": "Pavel",
                "films": [
                    {
                        "id": "cdc9baa8-df85-493f-a048-d2a8a642992d",
                        "roles": ["actor", "writer"],
                    }
                ],
            },
        ),
    ],
)
async def test_can_get_person_by_id(
    es_write_data: ESWriteType,
    make_get_request: GetRequestType,
    persons_access_token: str,
    person_id: uuid.UUID,
    expected_status: int,
    expected_data: dict,
) -> None:
    persons_es_data = [
        {"id": "72b4862d-d0c8-47bc-9775-4968e59764e0", "full_name": "Pavel"}
    ]

    movies_es_data = [
        {
            "id": "cdc9baa8-df85-493f-a048-d2a8a642992d",
            "imdb_rating": 8,
            "genres": [
                {"id": "63d4cbaa-79e7-4ee8-a215-1f87a8829e53", "name": "Action"},
            ],
            "title": "Harry Potter",
            "description": "magic",
            "directors_names": [],
            "actors_names": ["Pavel"],
            "writers_names": ["Pavel"],
            "directors": [],
            "actors": [
                {"id": "72b4862d-d0c8-47bc-9775-4968e59764e0", "full_name": "Pavel"}
            ],
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

    body, status = await make_get_request(
        f"{PERSONS_URL}/{person_id}", {}, persons_access_token
    )

    assert status == expected_status
    assert body == expected_data


@pytest.mark.parametrize(
    "person_id, expected_status, expected_data, expected_key",
    [
        (
            "e9c9baa8-df85-493f-a048-d2a8a642992d",
            HTTPStatus.OK,
            {
                "id": "e9c9baa8-df85-493f-a048-d2a8a642992d",
                "full_name": "Alena",
                "films": [
                    {"id": "abc9baa8-df85-493f-a048-d2a8a642992d", "roles": ["actor"]}
                ],
            },
            "fastapi-cache:person_details:49638137e3d630914cb0a06c158c7f02",
        ),
        (
            "72b4862d-d0c8-47bc-9775-4968e59764e0",
            HTTPStatus.OK,
            {
                "id": "72b4862d-d0c8-47bc-9775-4968e59764e0",
                "full_name": "Pavel",
                "films": [
                    {"id": "cdc9baa8-df85-493f-a048-d2a8a642992d", "roles": ["writer"]}
                ],
            },
            "fastapi-cache:person_details:372e27e2756ca7d2246f2f80f3cd88c7",
        ),
    ],
)
async def test_can_get_person_by_id_from_cache(
    es_write_data: ESWriteType,
    flushable_redis_client: Redis,
    make_get_request: GetRequestType,
    persons_access_token: str,
    person_id: uuid.UUID,
    expected_status: int,
    expected_data: dict[str, Any],
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

    _, status = await make_get_request(
        f"{PERSONS_URL}/{person_id}", {}, persons_access_token
    )

    assert status == expected_status

    raw_data = await flushable_redis_client.get(expected_key)
    assert json.loads(raw_data) == expected_data


@pytest.mark.parametrize(
    "person_id, expected_status, expected_data",
    [
        (
            "e9c9baa8-df85-493f-a048-d2a8a642992d",
            HTTPStatus.OK,
            [
                {
                    "id": "abc9baa8-df85-493f-a048-d2a8a642992d",
                    "imdb_rating": 9,
                    "title": "The Star",
                }
            ],
        ),
        (
            "72b4862d-d0c8-47bc-9775-4968e59764e0",
            HTTPStatus.OK,
            [
                {
                    "id": "cdc9baa8-df85-493f-a048-d2a8a642992d",
                    "imdb_rating": 8,
                    "title": "Harry Potter",
                }
            ],
        ),
    ],
)
async def test_can_get_person_films_by_id(
    es_write_data: ESWriteType,
    make_get_request: GetRequestType,
    persons_access_token: str,
    person_id: uuid.UUID,
    expected_status: int,
    expected_data: dict[str, Any],
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

    body, status = await make_get_request(
        f"{PERSONS_URL}/{person_id}/film", {}, persons_access_token
    )

    assert status == expected_status
    assert body == expected_data


async def test_can_get_unexistent_person_by_id(
    make_get_request: GetRequestType, persons_access_token: str
) -> None:
    _, status = await make_get_request(
        f"{PERSONS_URL}/{str(uuid.uuid4())}", {}, persons_access_token
    )

    assert status == HTTPStatus.NOT_FOUND
