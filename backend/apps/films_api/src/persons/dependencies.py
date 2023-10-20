from functools import lru_cache
from uuid import UUID

from fastapi import Depends
from src.common.database import get_elastic_handler
from src.common.utils import ESHandler, models_to_schemas
from src.films.schemas import Film
from src.persons import schemas
from src.persons.exceptions import PersonNotFound
from src.persons.params import PersonRequestParams
from src.persons.repository import ESPersonRepository
from src.persons.service import PersonService, StandardPersonService


@lru_cache()
def get_person_service(
    es_handler: ESHandler = Depends(get_elastic_handler),
) -> PersonService:
    person_repository = ESPersonRepository(es_handler)
    return StandardPersonService(person_repository)


async def get_person(
    person_id: UUID,
    service: PersonService = Depends(get_person_service),
) -> schemas.DetailPerson:
    person_model = await service.find_person_by_id(person_id)
    if person_model is None:
        raise PersonNotFound(person_id)

    return schemas.DetailPerson.from_model(person_model)


async def get_persons(
    request_params: PersonRequestParams = Depends(PersonRequestParams),
    service: PersonService = Depends(get_person_service),
) -> list[schemas.DetailPerson]:
    persons = await service.find_persons_by_params(request_params)
    return models_to_schemas(persons, schemas.DetailPerson)


async def get_person_films(
    person_id: UUID,
    service: PersonService = Depends(get_person_service),
) -> list[Film]:
    films = await service.find_person_related_movies(person_id)
    return models_to_schemas(films, Film)


async def get_searched_persons(
    request_params: PersonRequestParams = Depends(PersonRequestParams),
    service: PersonService = Depends(get_person_service),
) -> list[schemas.DetailPerson]:
    persons = await service.find_persons_by_params(request_params)
    return models_to_schemas(persons, schemas.DetailPerson)
