from abc import ABC, abstractmethod
from uuid import UUID

from src.films.models import Film
from src.films.params import FilmRequestParams
from src.films.repository import FilmRepository


class FilmService(ABC):
    @abstractmethod
    async def find_film_by_id(self, primary_key: UUID) -> Film | None:
        pass

    @abstractmethod
    async def find_films_by_params(self, params: FilmRequestParams) -> list[Film]:
        pass


class RecommendationService(ABC):
    @abstractmethod
    async def get_user_preferences(self, user_id: UUID) -> FilmRequestParams:
        pass


class StandardFilmService(FilmService):
    def __init__(self, film_repository: FilmRepository) -> None:
        super().__init__()
        self.film_repository = film_repository

    async def find_film_by_id(self, primary_key: UUID) -> Film | None:
        return await self.film_repository.find_by_id(primary_key)

    async def find_films_by_params(self, params: FilmRequestParams) -> list[Film]:
        db_params = params.to_db_params(self.film_repository.repository_type())
        return await self.film_repository.find_by_query(db_params)


class MockRecommendationService(RecommendationService):
    async def get_user_preferences(self, user_id: UUID) -> FilmRequestParams:
        """Mock method for getting user preferences.

        The function simulating the response from the recommendation service.
        The real service will use the user preferences to find the most relevant films.
        But for now we will return the default params.
        """
        return FilmRequestParams(query="Shooter", page_number=1, page_size=50)
