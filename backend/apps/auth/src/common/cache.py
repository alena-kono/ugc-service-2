from abc import ABC, abstractmethod
from typing import Any

from redis.asyncio import Redis as AsyncRedisClient


class AbstractCache(ABC):
    @abstractmethod
    async def exist(self, *keys) -> int:
        """Check that keys exist in cache."""
        raise NotImplementedError

    @abstractmethod
    async def get(self, key: str) -> Any:
        """Get data from cache by the key."""
        raise NotImplementedError

    @abstractmethod
    async def set(self, key: str, data: Any, timeout_secs: int | None = None) -> bool:
        """Save data (key: value) in cache with the given key and timeout."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, *keys) -> int:
        """Delete keys from cache."""
        raise NotImplementedError


class RedisCache(AbstractCache):
    """Redis cache implementation."""

    def __init__(self, redis_client: AsyncRedisClient):
        self.client = redis_client

    async def exist(self, *keys) -> int:
        return await self.client.exists(*keys)

    async def get(self, key: str) -> Any | None:
        return await self.client.get(key)

    async def set(self, key: str, data: Any, timeout_secs: int | None = None) -> bool:
        return bool(await self.client.set(name=key, value=data, ex=timeout_secs))

    async def delete(self, *keys) -> int:
        return await self.client.delete(*keys)
