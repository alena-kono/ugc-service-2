from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Generic, Type, TypeVar

from src.common.utils import ESHandler
from src.settings.app import AppSettings

settings = AppSettings.get()


T = TypeVar("T")


class RepositoryType(str, Enum):
    ES: str = "elastic"


class AbstractRepository(ABC, Generic[T]):
    @abstractmethod
    async def find_by_id(self, primary_key: Any) -> T | None:
        pass

    @abstractmethod
    async def find_by_query(self, query: dict[str, Any]) -> list[T]:
        pass

    @abstractmethod
    def repository_type(self) -> RepositoryType:
        pass


class ESRepository(AbstractRepository[T]):
    schema: Type[T]

    def __init__(self, es_handler: ESHandler, index: str) -> None:
        self.es_handler = es_handler
        self.index = index

    async def find_by_id(self, primary_key: Any) -> T | None:
        if item := await self.es_handler.get_by_id(self.index, str(primary_key)):
            return self.schema(**item)
        return None

    async def find_by_query(self, query: dict[str, Any]) -> list[T]:
        raw_entities = await self.es_handler.get(self.index, query)
        if not raw_entities:
            return []
        return [self.schema(**entity) for entity in raw_entities]

    def repository_type(self) -> RepositoryType:
        return RepositoryType.ES
