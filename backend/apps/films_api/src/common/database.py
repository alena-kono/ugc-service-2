from redis.asyncio import Redis
from src.common.utils import ESHandler

redis: None | Redis = None

es_handler: None | ESHandler = None


async def get_redis() -> Redis:
    if redis is None:
        raise RuntimeError("Redis client has not been defined.")

    return redis


async def get_elastic_handler() -> ESHandler:
    if es_handler is None:
        raise RuntimeError("Es handler has not been defined.")

    return es_handler
