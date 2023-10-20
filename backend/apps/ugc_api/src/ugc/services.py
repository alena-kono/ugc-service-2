from abc import ABC, abstractmethod

from src.ugc.message_queue import IMessageQueue
from src.ugc.schemas import BaseEvent, FilmProgressOutputMsg


class IEventService(ABC):
    @abstractmethod
    async def handle_event(self, topic: str, event: BaseEvent, user_id: str) -> None:
        """Method handle event from the client and send it to the queue.

        Args:
            event (str): Event to be handled.

        Returns:
            None: No return value.
        """


class EventService(IEventService):
    """Event service implementation."""

    event_message_class = FilmProgressOutputMsg

    def __init__(self, message_queue: IMessageQueue):
        self.message_queue = message_queue

    @staticmethod
    def build_event_message(event: BaseEvent, user_id: str) -> FilmProgressOutputMsg:
        return FilmProgressOutputMsg(
            user_id=user_id,
            film_id=event.film_id,
            progress_sec=event.progress_sec,
            timestamp=event.timestamp,
        )

    @staticmethod
    def build_key(film_id: str, user_id: str) -> str:
        return f"{user_id}{film_id}"

    async def handle_event(self, topic: str, event: BaseEvent, user_id: str) -> None:
        event_message = self.build_event_message(event=event, user_id=user_id)
        key = self.build_key(film_id=event.film_id, user_id=user_id)

        await self.message_queue.push(
            topic, event_message.json().encode(), key=key.encode()
        )
