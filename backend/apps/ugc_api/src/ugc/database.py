from redis.asyncio import Redis
from aiokafka import AIOKafkaProducer

redis: None | Redis = None
producer: AIOKafkaProducer | None = None


def get_redis() -> Redis:
    if redis is None:
        raise RuntimeError("Redis client has not been defined.")

    return redis


def get_kafka_producer() -> AIOKafkaProducer:
    if producer is None:
        raise RuntimeError("Kafka producer has not been defined.")

    return producer
