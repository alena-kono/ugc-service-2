import sqlite3
from abc import ABC, abstractmethod
from pathlib import Path
from types import TracebackType
from typing import Generator, Type

from loguru import logger
from sqlite_to_postgres.logic.data_types import TableData, TableType


class SQLiteExtractorInterface(ABC):
    @abstractmethod
    def extract_movies(self) -> Generator[TableData, None, None]:
        ...

    @abstractmethod
    def __init__(self, file_name: Path) -> None:
        ...

    @abstractmethod
    def __enter__(self) -> "SQLiteExtractor":
        ...

    @abstractmethod
    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        ...


class SQLiteExtractor(SQLiteExtractorInterface):
    TABLE_ORDER = [
        TableType.PERSON,
        TableType.GENRE,
        TableType.FILMWORK,
        TableType.GENREFILMWORK,
        TableType.PERSONFILMWORK,
    ]

    def __init__(self, file_name: Path, chunk_size: int = 50) -> None:
        self.chunk_size = chunk_size

        self.connection: sqlite3.Connection
        self.cursor: sqlite3.Cursor

        self.db_path = str(file_name)

    def connect(self) -> None:
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        logger.info("succesfully connected to sqlite dbms")

    def disconnect(self) -> None:
        self.connection.commit()
        self.connection.close()
        logger.info("succesfully disconnect from sqlite dbms")

    def __enter__(self) -> "SQLiteExtractor":
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.disconnect()

    def extract_movies(self) -> Generator[TableData, None, None]:
        for table in self.TABLE_ORDER:
            logger.info(f"fetching data from `{table.value}` table")

            self.cursor.execute(f"SELECT * FROM {table.value};")
            table_data = self.cursor.fetchmany(self.chunk_size)
            while table_data:
                logger.debug(
                    f"Retrieved {len(table_data)} rows from `{table.value}` table"
                )

                yield TableData(table_name=table, data=table_data)
                table_data = self.cursor.fetchmany(self.chunk_size)
