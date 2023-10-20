from abc import ABC, abstractmethod
from types import TracebackType
from typing import Iterable, Type, cast

import psycopg2
from loguru import logger
from psycopg2.errors import DataError
from psycopg2.extras import DictCursor, execute_values
from sqlite_to_postgres.logic.data_types import (
    FilmWork,
    GenericTable,
    Genre,
    GenreFilmwork,
    Person,
    PersonFilmWork,
    PGSettings,
    TableData,
    TableType,
)


class PostgresSaverInterface(ABC):
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
    def __enter__(self) -> "PostgresSaver":
        ...

    @abstractmethod
    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        ...

    @abstractmethod
    def save_all_data(self, data: TableData) -> None:
        ...


class PostgresSaver(ABC):
    TABLE_MAPPING: dict[str, Type[GenericTable]] = {
        TableType.PERSON.value: Person,
        TableType.PERSONFILMWORK.value: PersonFilmWork,
        TableType.GENRE.value: Genre,
        TableType.GENREFILMWORK.value: GenreFilmwork,
        TableType.FILMWORK.value: FilmWork,
    }

    def __init__(self, settings: PGSettings, chunk_size: int = 50) -> None:
        self.settings = settings
        self.chunk_size = chunk_size

    def connect(self) -> None:
        self.connection = psycopg2.connect(
            **self.settings.dict(), cursor_factory=DictCursor
        )
        logger.info("succesfully connected to postgre dbms")

    def disconnect(self) -> None:
        self.connection.close()
        logger.info("succesfully disconnect from postgre dbms")

    def __enter__(self) -> "PostgresSaver":
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.disconnect()

    @staticmethod
    def factory_table_data(table_data: TableData) -> list[GenericTable]:
        return [
            PostgresSaver.TABLE_MAPPING[cast(str, table_data.table_name)](**data)
            for data in table_data.data
        ]

    @staticmethod
    def get_insert_part(table_name: str, columns_names: Iterable[str]) -> str:
        insert_arguments = ",".join(columns_names)
        return f"INSERT INTO content.{table_name} ({insert_arguments})"

    @staticmethod
    def get_on_conflict_part(columns_names: Iterable[str]) -> str:
        set_arguments = ", ".join(
            f"{column}=EXCLUDED.{column}" for column in columns_names if "id" != column
        )
        return f"ON CONFLICT (id) DO UPDATE SET {set_arguments};"

    def build_upsert_query(self, table_name: str, columns_names: Iterable[str]) -> str:
        query = [
            self.get_insert_part(table_name, columns_names),
            "VALUES %s",
            self.get_on_conflict_part(columns_names),
        ]

        return "\n".join(query)

    def save_all_data(self, data: TableData) -> None:
        logger.debug(f"Inserting to {len(data.data)} rows  to {data.table_name}")

        with self.connection.cursor() as cursor:
            table_dataclasses = self.factory_table_data(table_data=data)
            query = self.build_upsert_query(
                cast(str, data.table_name), table_dataclasses[0].get_columns()
            )
            query_data = [data.get_rows() for data in table_dataclasses]

            try:
                execute_values(
                    cursor, query, query_data, template=None, page_size=self.chunk_size
                )
                self.connection.commit()
            except DataError as e:
                logger.error(f"data error \n {query=}, {query_data=}")
                logger.exception(e)
                self.connection.rollback()
