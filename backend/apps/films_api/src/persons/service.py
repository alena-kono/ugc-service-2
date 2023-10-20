from abc import ABC, abstractmethod
from uuid import UUID

from src.films.models import Film
from src.persons.models import Person, PersonFilm
from src.persons.params import PersonRequestParams
from src.persons.repository import PersonRepository


class PersonService(ABC):
    @abstractmethod
    async def find_person_by_id(self, primary_key: UUID) -> Person | None:
        pass

    @abstractmethod
    async def find_persons_by_params(self, params: PersonRequestParams) -> list[Person]:
        pass

    @abstractmethod
    async def find_person_related_movies(self, primary_ley: UUID) -> list[Film]:
        pass


class StandardPersonService(PersonService):
    def __init__(self, person_repository: PersonRepository) -> None:
        super().__init__()
        self.person_repository = person_repository

    async def find_person_by_id(self, primary_key: UUID) -> Person | None:
        person = await self.person_repository.find_by_id(primary_key)
        if not person:
            return None
        related_movies = await self.person_repository.find_people_related_movies_roles(
            [person.id]
        )
        self._map_person_movies([person], related_movies)
        return person

    async def find_person_related_movies(self, primary_ley: UUID) -> list[Film]:
        return await self.person_repository.find_person_related_movies(primary_ley)

    async def find_persons_by_params(self, params: PersonRequestParams) -> list[Person]:
        db_params = params.to_db_params(self.person_repository.repository_type())
        persons = await self.person_repository.find_by_query(db_params)
        if not persons:
            return []
        related_movies = await self.person_repository.find_people_related_movies_roles(
            [person.id for person in persons]
        )
        self._map_person_movies(persons, related_movies)
        return persons

    @staticmethod
    def _map_person_movies(persons: list[Person], movies: dict[UUID, list[PersonFilm]]):
        for person in persons:
            person.films = movies[person.id]
