from http import HTTPStatus
from typing import Any

import pytest
from tests.functional.conftest import ESWriteType, GetRequestType
from tests.functional.settings import Settings

pytestmark = pytest.mark.asyncio

settings = Settings.get()
PERSONS_SEARCH_URL = "/api/v1/persons/search"


@pytest.mark.parametrize(
    "query_data, expected_status, expected_data",
    [
        (
            {"query": "pavel funny", "page_size": 10, "page": 1},
            HTTPStatus.OK,
            [
                {
                    "id": "62b4862d-d0c8-47bc-9775-4968e59764e0",
                    "full_name": "Pavel funny developer",
                    "films": [],
                },
            ],
        ),
        (
            {"query": "teamlead alena", "page_size": 10, "page": 1},
            HTTPStatus.OK,
            [
                {
                    "id": "b9c9baa8-df85-493f-a048-d2a8a642992d",
                    "full_name": "Alena lovely teamlead",
                    "films": [],
                },
            ],
        ),
        (
            {
                "query": "nikita developer",
                "sort_by": "full_name",
                "order_by": "desc",
                "page_size": 10,
                "page": 1,
            },
            HTTPStatus.OK,
            [
                {
                    "id": "62b4862d-d0c8-47bc-9775-4968e59764e0",
                    "full_name": "Pavel funny developer",
                    "films": [],
                },
                {
                    "id": "a2b4862d-d0c8-47bc-9775-4968e59764e0",
                    "full_name": "Nikita interesting developer",
                    "films": [],
                },
            ],
        ),
        (
            {
                "query": "test empty query",
            },
            HTTPStatus.OK,
            [],
        ),
    ],
)
async def test_persons_search(
    es_write_data: ESWriteType,
    make_get_request: GetRequestType,
    persons_access_token: str,
    query_data: dict[str, Any],
    expected_status: int,
    expected_data: int,
) -> None:
    persons_es_data = [
        {
            "id": "b9c9baa8-df85-493f-a048-d2a8a642992d",
            "full_name": "Alena lovely teamlead",
        },
        {
            "id": "62b4862d-d0c8-47bc-9775-4968e59764e0",
            "full_name": "Pavel funny developer",
        },
        {
            "id": "a2b4862d-d0c8-47bc-9775-4968e59764e0",
            "full_name": "Nikita interesting developer",
        },
    ]

    await es_write_data(
        persons_es_data,
        settings.elastic.person_index.index,
        settings.elastic.person_index.field_id_name,
    )

    body, status = await make_get_request(
        PERSONS_SEARCH_URL, query_data, persons_access_token
    )

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
async def test_persons_search_can_handle_wrong_args(
    make_get_request: GetRequestType,
    persons_access_token: str,
    query_data: dict[str, str],
    expected_status: int,
) -> None:
    _, status = await make_get_request(
        PERSONS_SEARCH_URL, query_data, persons_access_token
    )

    assert status == expected_status
