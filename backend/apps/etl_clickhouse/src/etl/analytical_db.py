from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any

from asynch.connection import Connection
from asynch.cursors import DictCursor
from src.exceptions.exception import BatchInsertException


class AnalyticalRepository(ABC):
    "Interface for analytical database helpers. i.e clickhouse, vertica"

    @abstractmethod
    async def insert_batch(
        self, table: str, keys: Iterable[str], data: list[dict[str, Any]]
    ) -> None:
        pass


class ClickhouseRepository(AnalyticalRepository):
    KEYS_SEPARATOR = ","

    INSERT_BATCH_QUERY: str = "INSERT INTO {table} ({keys}) VALUES"

    def __init__(self, connection: Connection) -> None:
        super().__init__()
        self.connection = connection

    async def insert_batch(
        self, table: str, keys: Iterable[str], data: list[dict[str, Any]]
    ) -> None:
        try:
            async with self.connection.cursor(cursor=DictCursor) as cursor:
                query = self.__batch_insert_query(table, keys)
                await cursor.execute(query, data)
        # TODO: catch correct clickhouse exceptions and react if possible
        except Exception as e:
            raise BatchInsertException from e

    @staticmethod
    def __batch_insert_query(table: str, keys: Iterable[str]) -> str:
        keys_str = ClickhouseRepository.KEYS_SEPARATOR.join(keys)
        return ClickhouseRepository.INSERT_BATCH_QUERY.format(
            table=table, keys=keys_str
        )
