from functools import lru_cache
from uuid import UUID

from fastapi import Depends
from src.common.database import get_elastic_handler
from src.common.utils import ESHandler, models_to_schemas
from src.genres.exceptions import GenreNotFound
from src.genres.params import GenreRequestParams
from src.genres.repository import ESGenreRepository
from src.genres.schemas import Genre
from src.genres.service import GenreService, StandardGenreService


@lru_cache()
def get_genre_service(
    es_handler: ESHandler = Depends(get_elastic_handler),
) -> GenreService:
    genre_repository = ESGenreRepository(es_handler)
    return StandardGenreService(genre_repository)


async def get_genre(
    genre_id: UUID,
    service: GenreService = Depends(get_genre_service),
) -> Genre:
    genre_model = await service.find_genre_by_id(genre_id)
    if genre_model is None:
        raise GenreNotFound(genre_id)

    return Genre.from_model(genre_model)


async def get_genres(
    request_params: GenreRequestParams = Depends(GenreRequestParams),
    service: GenreService = Depends(get_genre_service),
) -> list[Genre]:
    genres = await service.find_genres_by_params(request_params)
    return models_to_schemas(genres, Genre)


async def get_searched_genres(
    request_params: GenreRequestParams = Depends(GenreRequestParams),
    service: GenreService = Depends(get_genre_service),
) -> list[Genre]:
    genres = await service.find_genres_by_params(request_params)
    return models_to_schemas(genres, Genre)
