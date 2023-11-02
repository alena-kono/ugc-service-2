import logging

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from src.buffer.flush_buffer import get_flushable_buffer
from src.etl import clickhouse_connection
from src.etl.analytical_db import ClickhouseRepository
from src.etl.topic_handler import TopicMessage, get_topic_handler
from src.settings.app import AppSettings

logger = logging.getLogger(__name__)


async def run_etl(app_settings: AppSettings):
    logger.info("Starting clickhouse etl")

    async with clickhouse_connection.create_connection_pool(
        app_settings.clickhouse
    ) as connection_pool, AIOKafkaConsumer(
        app_settings.kafka.topic,
        bootstrap_servers=[app_settings.kafka.dsn],
        group_id=app_settings.kafka.consumer_group_id,
        auto_offset_reset="latest",
        enable_auto_commit=False,
    ) as consumer, AIOKafkaProducer(
        bootstrap_servers=[app_settings.kafka.dsn],
        compression_type="gzip",
        enable_idempotence=True,
        max_batch_size=32768,
        linger_ms=500,
    ) as producer, get_flushable_buffer(
        max_buffer_size=app_settings.etl.buffer_size
    ) as buffer:
        clickhouse_connection.connection_pool = connection_pool

        async with clickhouse_connection.clickhouse_connection() as connection:
            message_handler = get_topic_handler(
                topic=app_settings.kafka.topic,
                consumer=consumer,
                producer=producer,
                dlq_topic=app_settings.kafka.dlq,
                repository=ClickhouseRepository(connection),
                db_table=app_settings.clickhouse.table,
            )

            buffer.add_on_flush_callback(message_handler.handle_batch)

            logger.info(
                f"Starting to consume data from topic = {app_settings.kafka.topic}"
            )

            async for message in consumer:
                logger.info(
                    f"""Consumed new message from topic = {app_settings.kafka.topic}, partition = {message.partition},
                    offset = {message.offset}, timestamp = {message.timestamp}, checksum = {message.checksum}"""
                )
                topic_message = TopicMessage(key=message.key, value=message.value)
                await buffer.push(topic_message, len(message.value))
