import logging
from abc import ABC, abstractmethod
from enum import StrEnum, unique

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from pydantic import BaseModel
from src.etl.analytical_db import AnalyticalRepository
from src.exceptions.exception import BatchInsertException
from src.models.base import AppBaseSchema
from src.models.view import ViewMessage

logger = logging.getLogger(__name__)


@unique
class Topic(StrEnum):
    VIEWS: str = "views"


TOPIC_SCHEMAS_MAP: dict[str, type[AppBaseSchema]] = {Topic.VIEWS: ViewMessage}


class TopicMessage(BaseModel):
    key: bytes | None
    value: bytes


class ITopicHandler(ABC):
    "Interface for different topics message handlers"

    @abstractmethod
    async def handle_batch(self, messages: list[TopicMessage]) -> None:
        pass


class KafkaTopicHandler(ITopicHandler):
    def __init__(
        self,
        schema: type[AppBaseSchema],
        consumer: AIOKafkaConsumer,
        producer: AIOKafkaProducer,
        dlq_topic: str,
    ) -> None:
        super().__init__()
        # TODO: replace with avro schema
        self.schema = schema
        self.consumer = consumer
        self.producer = producer
        self.dlq_topic = dlq_topic

    def parse_messages(self, messages: list[TopicMessage]) -> tuple:
        parsed_messages = []
        dlq_messages = []

        for message in messages:
            logger.debug(f"Parsing message = {message}, schema = {self.schema}")
            try:
                view = self.schema.parse_raw(message.value)
                parsed_messages.append(view)
            except Exception as e:
                logger.error(
                    f"Couldn't parse message = {message}, err = {e}", exc_info=True
                )
                dlq_messages.append(message)

        return parsed_messages, dlq_messages

    async def send_to_dlq(self, dlq_messages: list[TopicMessage]) -> None:
        if not dlq_messages:
            return

        logger.warning(f"Sending {self.schema} to dlq, n = {len(dlq_messages)}")
        for dlq_message in dlq_messages:
            try:
                await self.producer.send(
                    topic=self.dlq_topic,
                    # Use the same key so we can guarantee the same order during reprocessing
                    key=dlq_message.key,
                    value=dlq_message.value,
                )
            except Exception as e:
                # Just ignore the error as we still can proceed even if we can't send a message to dlq
                logger.error(
                    f"Something went wrong, couldn't send message = {dlq_message.value!r} to dlq = {self.dlq_topic}, err = {e}"
                )

    async def handle_batch(self, messages: list[TopicMessage]) -> None:
        # Need to override the method so class can be instantiated and tested
        raise NotImplementedError


class KafkaToDatabaseHandler(KafkaTopicHandler):
    def __init__(
        self,
        schema: type[AppBaseSchema],
        consumer: AIOKafkaConsumer,
        producer: AIOKafkaProducer,
        dlq_topic: str,
        analytical_repository: AnalyticalRepository,
        db_table: str,
    ) -> None:
        super().__init__(schema, consumer, producer, dlq_topic)
        self.analytical_repository = analytical_repository
        self.db_table = db_table

    async def handle_batch(self, messages: list[TopicMessage]) -> None:
        logger.info(f"Handling {self.schema} kafka messages, n = {len(messages)}")
        models, dlq_messages = self.parse_messages(messages)
        if models:
            logger.info(f"Sending {self.schema} to clickhouse, n = {len(models)}")

            try:
                await self.analytical_repository.insert_batch(
                    table=self.db_table,
                    keys=models[0].dict().keys(),
                    data=[model.dict() for model in models],
                )
            except BatchInsertException as e:
                logger.error(
                    f"Couldn't insert batch {self.schema}, n = {len(models)}, err = {e}"
                )
                # if insert failed we need to reprocess all messages later
                dlq_messages = messages

        await self.send_to_dlq(dlq_messages)

        await self.consumer.commit()


def get_topic_handler(
    *,
    topic: str,
    consumer: AIOKafkaConsumer,
    producer: AIOKafkaProducer,
    dlq_topic: str,
    repository: AnalyticalRepository,
    db_table: str,
) -> ITopicHandler:
    schema = TOPIC_SCHEMAS_MAP.get(topic, None)

    if not schema:
        raise ValueError(f"No schema configured for topic = {topic}")

    return KafkaToDatabaseHandler(
        schema=schema,
        consumer=consumer,
        producer=producer,
        dlq_topic=dlq_topic,
        analytical_repository=repository,
        db_table=db_table,
    )
