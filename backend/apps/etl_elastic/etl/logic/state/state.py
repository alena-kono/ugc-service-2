from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import cast

from etl.logic.backoff.backoff import etl_backoff
from etl.logic.storage.storage import Storage
from etl.settings.settings import RedisSettings
from loguru import logger
from pydantic import BaseModel
from redis import Redis


class StateData(BaseModel):
    last_checkup: datetime | None


class StateInt(ABC):
    storage: Storage
    output_topic: str

    @abstractmethod
    def __init__(self, path: Path) -> None:
        ...

    @abstractmethod
    def publish_state(self) -> None:
        ...

    @abstractmethod
    def store_state(self) -> None:
        ...

    @abstractmethod
    def update_state(self) -> None:
        ...


class RedisState(StateInt):
    origin_date = datetime(year=2000, month=1, day=1)
    state_name = "etl_last_checkup"

    output_topic = "last_checkup"
    storage = Storage()

    def __init__(self, settings: RedisSettings) -> None:
        self.state = StateData(last_checkup=None)

        self.redis = Redis(host=settings.host, port=settings.port)
        self.redis_key = f"{settings.prefix}_{self.state_name}"

    @etl_backoff()
    def publish_state(self) -> None:
        logger.info("Reading the state")

        last_checkup = self.redis.get(self.redis_key)
        if last_checkup is None:
            self.state = StateData(last_checkup=self.origin_date)
        else:
            self.state = StateData(last_checkup=cast(datetime, last_checkup))

        self.storage.set_value(self.output_topic, self.state.last_checkup)

    def update_state(self) -> None:
        logger.info("Updating the state")

        self.state = StateData(last_checkup=datetime.utcnow())

    @etl_backoff()
    def store_state(self) -> None:
        logger.info("Storing the state")

        self.redis.set(self.redis_key, str(self.state.last_checkup))
