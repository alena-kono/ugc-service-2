from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache
from src.films import schemas as film_schemas
from src.persons import schemas as person_schemas
from src.persons.dependencies import (
    get_person,
    get_person_films,
    get_persons,
    get_searched_persons,
)
from src.persons.settings import PersonSettings

person_settings = PersonSettings.get()

router = APIRouter()


@router.get(
    path="/{person_id:uuid}",
    response_model=person_schemas.DetailPerson,
    summary="Person by id",
    description="Get person by its id",
    response_description="Person id, full name and related films",
)
@cache(expire=person_settings.cache_expire_in_seconds, namespace="person_details")
async def person_details(
    person: person_schemas.DetailPerson = Depends(get_person),
) -> person_schemas.DetailPerson:
    """Get person details.

    Example:
    `GET /api/v1/persons/8fb635c2-913f-4e70-bfec-404a5c7f7646`.
    """
    return person


@router.get(
    path="/{person_id:uuid}/film",
    response_model=list[film_schemas.Film],
    summary="Films by person id",
    description="Get films by person id",
    response_description="Film id, title and rating",
)
@cache(expire=person_settings.cache_expire_in_seconds, namespace="person_films")
async def person_films(
    films: list[film_schemas.Film] = Depends(get_person_films),
) -> list[film_schemas.Film]:
    """Get films by person id.

    Example:
    `GET /api/v1/persons/8fb635c2-913f-4e70-bfec-404a5c7f7646/film`.
    """
    return films


@router.get(
    path="",
    response_model=list[person_schemas.DetailPerson],
    summary="Persons list",
    description="Get paginated persons list sorted by full name by default",
    response_description="Person id, full name and related films",
)
@cache(expire=person_settings.cache_expire_in_seconds, namespace="persons")
async def persons_list(
    persons: list[person_schemas.DetailPerson] = Depends(get_persons),
) -> list[person_schemas.DetailPerson]:
    """Get list of persons.

    Example:
    `GET /api/v1/persons?sort_by=full_name&order_by=asc&page_number=1&page_size=50`.
    """
    return persons


@router.get(
    path="/search",
    response_model=list[person_schemas.DetailPerson],
    summary="Search persons",
    description="Full text search for persons",
    response_description="Person id, full name and related films",
)
@cache(expire=person_settings.cache_expire_in_seconds, namespace="persons_search")
async def person_search(
    persons: list[person_schemas.DetailPerson] = Depends(get_searched_persons),
) -> list[person_schemas.DetailPerson]:
    """Search for persons.

    Example:
    `GET /api/v1/persons/search?query=george`.
    """
    return persons
