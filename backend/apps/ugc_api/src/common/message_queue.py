import asyncio
from abc import ABC, abstractmethod

from aiokafka import AIOKafkaProducer
from async_timeout import timeout
from fastapi import HTTPException


def build_key(film_id: str, user_id: str) -> str:
    return f"{user_id}{film_id}"


class IMessageQueue(ABC):
    @abstractmethod
    async def push(self, topic: str, message: bytes, key: bytes | None = None) -> None:
        """Method push to the tail of the list the data passed as an argument.

        Args:
            data (str): Data to be pushed to the tail of the list.

        Returns:
            None: No return value.
        """


class KafkaMessageQueue(IMessageQueue):
    """Redis implementation."""

    TIMEOUT_SECONDS = 10

    def __init__(self, kafka_producer: AIOKafkaProducer):
        self.producer = kafka_producer

    async def push(self, topic: str, message: bytes, key: bytes | None = None) -> None:
        try:
            async with timeout(self.TIMEOUT_SECONDS):
                await self.producer.send(topic, message, key=key)
        except asyncio.TimeoutError as e:
            raise HTTPException(status_code=500, detail="Kafka is not available") from e
