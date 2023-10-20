from abc import ABC, abstractmethod
from types import TracebackType
from typing import Type

import psycopg2
from etl.settings.settings import PGSettings
from loguru import logger
from psycopg2._psycopg import connection as pg_connection
from psycopg2.extras import DictCursor


class PostgreClientInt(ABC):
    @abstractmethod
    def __init__(self, settings: PGSettings) -> None:
        ...

    @abstractmethod
    def connect(self) -> None:
        ...

    @abstractmethod
    def disconnect(self) -> None:
        ...

    @abstractmethod
    def __enter__(self) -> "PostgreClient":
        ...

    @abstractmethod
    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        ...


class PostgreClient(PostgreClientInt):
    connection: pg_connection

    def __init__(self, settings: PGSettings) -> None:
        self.settings = settings

    def connect(self) -> None:
        self.connection = psycopg2.connect(
            **self.settings.dict(), cursor_factory=DictCursor
        )
        logger.info("succesfully connected to the Postgre DBMS")

    def disconnect(self) -> None:
        self.connection.close()
        logger.info("succesfully disconnected from the Postgre DBMS")

    def __enter__(self) -> "PostgreClient":
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.disconnect()
