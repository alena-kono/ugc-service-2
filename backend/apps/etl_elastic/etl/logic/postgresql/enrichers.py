from abc import ABC, abstractmethod
from functools import lru_cache
from itertools import chain
from typing import cast
from uuid import UUID

from etl.logic.storage.storage import Storage
from loguru import logger
from psycopg2._psycopg import connection as pg_connection


class EnricherInt(ABC):
    @abstractmethod
    def enrich(self, connection: pg_connection) -> None:
        ...


class BaseEnricher(EnricherInt):
    input_topic: str
    output_topic: str

    storage = Storage()

    id_field: str | None = None
    join_table_name: str | None = None
    join_on_field: str | None = None

    def get_query(self) -> str:
        query = f"""
        --sql
        SELECT DISTINCT fw.id, fw.modified
        FROM content.film_work AS fw
        LEFT JOIN {self.join_table_name} ON
        {self.join_table_name}.{self.join_on_field} = fw.id
        WHERE {self.join_table_name}.{self.id_field} IN %s
        ORDER BY fw.modified;
        """
        return query

    def enrich(self, connection: pg_connection) -> None:
        logger.debug("Getting all modified films ids from the last checkup")

        producer_ids: list[list[UUID]] = self.storage.get(self.input_topic)
        if not producer_ids:
            return

        flat_ids = tuple(chain(*producer_ids))
        query = self.get_query()
        with connection.cursor() as cursor:
            cursor.execute(query, vars=(flat_ids,))
            enriched_ids = [res["id"] for res in cursor.fetchall()]

        self.storage.set_value(self.output_topic, enriched_ids)


class PersonFilmEnricher(BaseEnricher):
    input_topic = "person_ids"
    output_topic = "film_ids"

    id_field = "person_id"
    join_table_name = "content.person_film_work"
    join_on_field = "film_work_id"


class GenreFilmEnricher(BaseEnricher):
    input_topic = "genre_ids"
    output_topic = "film_ids"

    id_field = "genre_id"
    join_table_name = "content.genre_film_work"
    join_on_field = "film_work_id"


@lru_cache
def get_enrichers() -> list[EnricherInt]:
    enrichers = [enricher() for enricher in BaseEnricher.__subclasses__()]
    return cast(list[EnricherInt], enrichers)


def run_enrichers(connection: pg_connection) -> None:
    for enricher in get_enrichers():
        enricher.enrich(connection)
