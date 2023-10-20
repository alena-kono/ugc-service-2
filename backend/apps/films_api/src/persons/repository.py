from abc import abstractmethod
from collections import defaultdict
from typing import Any, AsyncGenerator, Type
from uuid import UUID

from src.common.repository import AbstractRepository, ESRepository
from src.common.utils import ESHandler
from src.films.models import Film
from src.films.settings import FilmSettings
from src.persons.models import Person, PersonFilm, RoleType
from src.persons.settings import PersonSettings

persons_settings = PersonSettings.get()
movies_settings = FilmSettings.get()


class PersonRepository(AbstractRepository[Person]):
    @abstractmethod
    async def find_people_related_movies_roles(
        self, people_primary_keys: list[UUID]
    ) -> dict[UUID, list[PersonFilm]]:
        pass

    @abstractmethod
    async def find_person_related_movies(self, primary_key: UUID) -> list[Film]:
        pass


class ESPersonRepository(ESRepository[Person], PersonRepository):
    schema: Type = Person

    def __init__(self, es_handler: ESHandler) -> None:
        super().__init__(es_handler, persons_settings.elastic_index)

    async def find_person_related_movies(self, primary_key: UUID) -> list[Film]:
        return [
            Film(**raw_movie)
            async for raw_movie in self._get_related_movies([primary_key])
        ]

    async def find_people_related_movies_roles(
        self, people_primary_keys: list[UUID]
    ) -> dict[UUID, list[PersonFilm]]:
        related_movies = defaultdict(lambda: [])
        async for raw_movie in self._get_related_movies(people_primary_keys):
            movie = Film(**raw_movie)
            actor_ids = [actor.id for actor in movie.actors]
            writers_ids = [writer.id for writer in movie.writers]
            director_ids = [director.id for director in movie.directors]
            for person_id in people_primary_keys:
                movie_roles = []
                if person_id in actor_ids:
                    movie_roles.append(RoleType.ACTOR)
                if person_id in writers_ids:
                    movie_roles.append(RoleType.WRITER)
                if person_id in director_ids:
                    movie_roles.append(RoleType.DIRECTOR)

                if movie_roles:
                    related_movies[person_id].append(
                        PersonFilm(id=movie.id, roles=movie_roles)
                    )
        return related_movies

    async def _get_related_movies(
        self, people_primary_keys: list[UUID]
    ) -> AsyncGenerator[dict[str, Any], None]:
        related_movies_query = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "nested": {
                                "path": "actors",
                                "query": {"terms": {"actors.id": people_primary_keys}},
                            }
                        },
                        {
                            "nested": {
                                "path": "writers",
                                "query": {"terms": {"writers.id": people_primary_keys}},
                            }
                        },
                        {
                            "nested": {
                                "path": "directors",
                                "query": {
                                    "terms": {"directors.id": people_primary_keys}
                                },
                            }
                        },
                    ]
                }
            }
        }
        async for raw_movie in self.es_handler.scan(
            movies_settings.elastic_index, related_movies_query
        ):
            yield raw_movie
