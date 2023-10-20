from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache
from src.films import schemas
from src.films.dependencies import (
    get_film,
    get_films,
    get_personalized_films,
    get_searched_films,
)
from src.films.settings import FilmSettings

film_settings = FilmSettings.get()

router = APIRouter()


@router.get(
    path="/{film_id:uuid}",
    response_model=schemas.DetailFilm,
    summary="Film by id",
    description="Get film by its id",
    response_description="Film id, title and rating",
)
@cache(expire=film_settings.cache_expire_in_seconds, namespace="film_details")
async def film_details(
    film: schemas.DetailFilm = Depends(get_film),
) -> schemas.DetailFilm:
    """Get film details.

    Example:
    `GET /api/v1/films/2a090dde-f688-46fe-a9f4-b781a985275e`.
    """
    return film


@router.get(
    path="",
    response_model=list[schemas.Film],
    summary="Films list",
    description="Get paginated films list sorted by rating by default",
    response_description="Film id, title and rating",
)
@cache(expire=film_settings.cache_expire_in_seconds, namespace="films")
async def films_list(
    films: list[schemas.Film] = Depends(get_films),
) -> list[schemas.Film]:
    """Get list of films.

    Example:
    `GET /api/v1/films?page_number=1&page_size=50&sort_by=imdb_rating&order_by=desc`.
    """
    return films


@router.get(
    path="/personalized",
    response_model=list[schemas.Film],
    summary="Personalized films list",
    description="Get paginated personalized films list sorted by rating by default",
    response_description="Film id, title and rating",
)
@cache(expire=film_settings.cache_expire_in_seconds, namespace="films_personalized")
async def personalized_films_list(
    films: list[schemas.Film] = Depends(get_personalized_films),
) -> list[schemas.Film]:
    """Get list of films.

    Example:
    `GET /api/v1/films/personalized?page_number=1&page_size=50&sort_by=imdb_rating&order_by=desc`.
    """
    return films


@router.get(
    path="/search",
    response_model=list[schemas.Film],
    summary="Search films",
    description="Full text search for films",
    response_description="Film id, title and rating",
)
@cache(expire=film_settings.cache_expire_in_seconds, namespace="films_search")
async def film_search(
    films: list[schemas.Film] = Depends(get_searched_films),
) -> list[schemas.Film]:
    """Search for films.

    Example:
    `GET /api/v1/films/search?query=star&page_number=1&page_size=50&sort_by=imdb_rating&order_by=desc`.
    """
    return films
