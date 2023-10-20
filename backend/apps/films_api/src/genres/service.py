from abc import ABC, abstractmethod
from uuid import UUID

from src.genres.models import Genre
from src.genres.params import GenreRequestParams
from src.genres.repository import GenreRepository


class GenreService(ABC):
    @abstractmethod
    async def find_genre_by_id(self, primary_key: UUID) -> Genre | None:
        pass

    @abstractmethod
    async def find_genres_by_params(self, params: GenreRequestParams) -> list[Genre]:
        pass


class StandardGenreService(GenreService):
    def __init__(self, genre_repository: GenreRepository) -> None:
        super().__init__()
        self.genre_repository = genre_repository

    async def find_genre_by_id(self, primary_key: UUID) -> Genre | None:
        return await self.genre_repository.find_by_id(primary_key)

    async def find_genres_by_params(self, params: GenreRequestParams) -> list[Genre]:
        db_params = params.to_db_params(self.genre_repository.repository_type())
        return await self.genre_repository.find_by_query(db_params)
