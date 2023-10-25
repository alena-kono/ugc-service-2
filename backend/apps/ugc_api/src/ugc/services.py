from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type
from src.ugc.message_queue import IMessageQueue, build_key
from src.ugc.input_schemas import (
    InputBaseSchema,
    FilmProgressEvent,
    LikeEvent,
    CommentEvent,
)
from src.ugc.output_schemas import (
    OutputBaseSchema,
    FilmProgressSchema,
    LikeSchema,
    CommentSchema,
)
from src.ugc.repositories import IRepository
import asyncio


InputSchemaType = TypeVar("InputSchemaType", bound=InputBaseSchema)
OutputSchemaType = TypeVar("OutputSchemaType", bound=OutputBaseSchema)


def build_output_schema_from(
    input_schema: InputBaseSchema, user_id: str
) -> OutputBaseSchema:
    """Build output schema from input schema."""
    mapping: dict[Type[InputBaseSchema], Type[OutputBaseSchema]] = {
        FilmProgressEvent: FilmProgressSchema,
        LikeEvent: LikeSchema,
        CommentEvent: CommentSchema,
    }

    input_schema_type = type(input_schema)

    return mapping[input_schema_type].from_input_schema(input_schema, user_id)


class IEventService(ABC, Generic[InputSchemaType, OutputSchemaType]):
    @abstractmethod
    async def handle_event(
        self,
        topic: str,
        input_schema: InputSchemaType,
        output_schema_class: Type[OutputSchemaType],
        user_id: str,
    ) -> OutputSchemaType:
        """Method handle event from the client and send it to the queue.

        Args:
            event (str): Event to be handled.

        Returns:
            None: No return value.
        """


class EventService(IEventService, Generic[InputSchemaType, OutputSchemaType]):
    """Event service implementation."""

    def __init__(self, message_queue: IMessageQueue, repository: IRepository):
        self.message_queue = message_queue
        self.repository = repository

    async def handle_event(
        self,
        topic: str,
        input_schema: InputSchemaType,
        output_schema_class: Type[OutputSchemaType],
        user_id: str,
    ) -> OutputSchemaType:
        output_schema = output_schema_class.from_input_schema(input_schema, user_id)
        key = build_key(film_id=input_schema.film_id, user_id=user_id)

        _, entity_id = await asyncio.gather(
            self.message_queue.push(
                topic, output_schema.json().encode(), key=key.encode()
            ),
            self.repository.insert(output_schema.dict(), collection=str(topic)),
        )
        
        stored_instance = await self.repository.get_by_id(entity_id, collection=str(topic))
        return output_schema_class(**stored_instance)
