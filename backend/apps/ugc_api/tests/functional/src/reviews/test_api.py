from time import time
from uuid import uuid4
import pytest

from httpx import AsyncClient
from motor.core import AgnosticClient
from src.common.authorization import JwtClaims
from src.settings.app import get_app_settings


pytestmark = pytest.mark.asyncio


settings = get_app_settings()


async def test_create_review(client: AsyncClient, db_session: AgnosticClient):
    test_event = {
        "film_id": str(uuid4()),
        "text": "test review",
        "timestamp": int(time()),
    }
    response = await client.post(
        "/reviews",
        json=test_event,
        headers={"X-Request-Id": "test", "Authorization": "Bearer test_jwt"},
    )

    assert response.status_code == 200

    created_event = response.json()
    assert created_event["film_id"] == test_event["film_id"]
    assert created_event["timestamp"] == test_event["timestamp"]
    assert created_event["text"] == test_event["text"]

    film_collection = db_session[settings.mongo.db_name]["reviews"]
    stored_event = film_collection.find_one(test_event)

    assert stored_event is not None


async def test_get_review(
    mock_jwt: JwtClaims, client: AsyncClient, db_session: AgnosticClient
):
    test_event = {
        "user_id": str(mock_jwt.user.id),
        "film_id": str(uuid4()),
        "text": "test review",
        "timestamp": int(time()),
    }

    film_collection = db_session[settings.mongo.db_name]["reviews"]
    await film_collection.insert_one(test_event)

    response = await client.get(
        f"/reviews?film_id={test_event['film_id']}",
        headers={"X-Request-Id": "test", "Authorization": "Bearer test_jwt"},
    )
    print(response.json())
    assert response.status_code == 200

    created_event = response.json()

    items = created_event["items"]
    assert len(items) == 1

    item = items[0]
    assert item["film_id"] == test_event["film_id"]
    assert item["text"] == test_event["text"]
    assert item["timestamp"] == test_event["timestamp"]
