from aiokafka import AIOKafkaProducer
from motor.core import AgnosticClient
from redis.asyncio import Redis

redis: None | Redis = None
producer: AIOKafkaProducer | None = None
mongodb: AgnosticClient | None = None


def get_mongodb() -> AgnosticClient:
    if mongodb is None:
        raise RuntimeError("MongoDB client has not been defined.")

    return mongodb


def get_redis() -> Redis:
    if redis is None:
        raise RuntimeError("Redis client has not been defined.")

    return redis


def get_kafka_producer() -> AIOKafkaProducer:
    if producer is None:
        raise RuntimeError("Kafka producer has not been defined.")

    return producer
