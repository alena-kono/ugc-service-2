from time import time
from uuid import uuid4
import pytest

from httpx import AsyncClient
from motor.core import AgnosticClient
from src.common.authorization import JwtClaims
from src.settings.app import get_app_settings


pytestmark = pytest.mark.asyncio


settings = get_app_settings()


async def test_create_film_progress(client: AsyncClient, db_session: AgnosticClient):
    test_event = {
        "film_id": str(uuid4()),
        "timestamp": time(),
        "progress_sec": 1,
    }
    response = await client.post(
        "/films-progresses",
        json=test_event,
        headers={"X-Request-Id": "test", "Authorization": "Bearer test_jwt"},
    )

    assert response.status_code == 200

    created_event = response.json()
    assert created_event["film_id"] == test_event["film_id"]
    assert created_event["timestamp"] == test_event["timestamp"]
    assert created_event["progress_sec"] == test_event["progress_sec"]

    film_collection = db_session[settings.mongo.db_name]["film_progress"]
    stored_event = film_collection.find_one(test_event)

    assert stored_event is not None


async def test_get_films(
    mock_jwt: JwtClaims, client: AsyncClient, db_session: AgnosticClient
):
    test_event = {
        "user_id": str(mock_jwt.user.id),
        "film_id": str(uuid4()),
        "timestamp": time(),
        "progress_sec": 1,
    }

    film_collection = db_session[settings.mongo.db_name]["film_progress"]
    await film_collection.insert_one(test_event)

    response = await client.get(
        "/films-progresses",
        headers={"X-Request-Id": "test", "Authorization": "Bearer test_jwt"},
    )

    assert response.status_code == 200

    created_event = response.json()
    assert len(created_event["items"]) == 1

    item = created_event["items"][0]
    assert item["film_id"] == test_event["film_id"]
    assert item["timestamp"] == test_event["timestamp"]
    assert item["progress_sec"] == test_event["progress_sec"]
