from functools import lru_cache
from logging import getLogger
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from src.common.database import get_elastic_handler
from src.common.dependencies import check_permission
from src.common.permission import Permissions
from src.common.schemas import JwtClaims
from src.common.utils import ESHandler, models_to_schemas
from src.films.exceptions import FilmNotFound
from src.films.params import FilmRequestParams
from src.films.repository import ESFilmRepository
from src.films.schemas import DetailFilm, Film
from src.films.service import (
    FilmService,
    MockRecommendationService,
    StandardFilmService,
)

logger = getLogger("root")

CanReadFilms = Annotated[
    JwtClaims | None, Depends(check_permission(Permissions.can_read_films))
]


@lru_cache()
def get_film_service(
    es_handler: ESHandler = Depends(get_elastic_handler),
) -> FilmService:
    film_repository = ESFilmRepository(es_handler)
    return StandardFilmService(film_repository)


async def get_film(
    film_id: UUID,
    service: FilmService = Depends(get_film_service),
) -> DetailFilm:
    film_model = await service.find_film_by_id(film_id)
    if film_model is None:
        raise FilmNotFound(film_id)

    return DetailFilm.from_model(film_model)


async def get_films(
    request_params: FilmRequestParams = Depends(FilmRequestParams),
    service: FilmService = Depends(get_film_service),
):
    film_models = await service.find_films_by_params(request_params)
    return models_to_schemas(film_models, Film)


async def get_searched_films(
    request_params: FilmRequestParams = Depends(FilmRequestParams),
    service: FilmService = Depends(get_film_service),
):
    film_models = await service.find_films_by_params(request_params)
    return models_to_schemas(film_models, Film)


async def get_personalized_films(
    token: CanReadFilms,
    film_service: FilmService = Depends(get_film_service),
    recommendation_service: MockRecommendationService = Depends(
        MockRecommendationService
    ),
):
    user_id = UUID(token.user.id)
    request_params = await recommendation_service.get_user_preferences(user_id)
    film_models = await film_service.find_films_by_params(request_params)
    return models_to_schemas(film_models, Film)
