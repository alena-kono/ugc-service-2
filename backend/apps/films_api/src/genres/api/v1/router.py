from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache
from src.genres import schemas
from src.genres.dependencies import get_genre, get_genres, get_searched_genres
from src.genres.settings import GenreSettings

genre_settings = GenreSettings.get()

router = APIRouter()


@router.get(
    path="/{genre_id:uuid}",
    response_model=schemas.Genre,
    summary="Genre by id",
    description="Get genre by its id",
    response_description="Genre id and name",
)
@cache(expire=genre_settings.cache_expire_in_seconds, namespace="genre_details")
async def genre_details(
    genre: schemas.Genre = Depends(get_genre),
) -> schemas.Genre:
    """Get genre details.

    Example:
    `GET /api/v1/genres/3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff`.
    """
    return genre


@router.get(
    path="",
    response_model=list[schemas.Genre],
    summary="Genres list",
    description="Get paginated genres list sorted by name by default",
    response_description="Genre id and name",
)
@cache(expire=genre_settings.cache_expire_in_seconds, namespace="genres")
async def genres(
    genres: list[schemas.Genre] = Depends(get_genres),
) -> list[schemas.Genre]:
    """Get list of genres.

    Example:
    `GET /api/v1/genres?sort_by=name&order_by=asc`.
    """
    return genres


@router.get(
    path="/search",
    response_model=list[schemas.Genre],
    summary="Search genres",
    description="Full text search for genres",
    response_description="Genre id and name",
)
@cache(expire=genre_settings.cache_expire_in_seconds, namespace="genres_search")
async def genre_search(
    genres: list[schemas.Genre] = Depends(get_searched_genres),
) -> list[schemas.Genre]:
    """Search for genres.

    Example:
    `GET /api/v1/genres/search?query=action`.
    """
    return genres
