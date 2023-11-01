import asyncio
from abc import ABC, abstractmethod

from fastapi_pagination import Page, Params
from src.common.dependencies import MessageQueueType, RepositoryType
from src.common.message_queue import IMessageQueue, build_key
from src.common.repositories import IRepository
from src.film_progress.schemas import (
    FilmProgressCreateRequestSchema,
    FilmProgressCreateResponseSchema,
    FilmProgressResponseSchema,
)


class IFilmProgressService(ABC):
    @abstractmethod
    async def create_film_progress(
        self, create_request_body: FilmProgressCreateRequestSchema, user_id: str
    ) -> FilmProgressCreateResponseSchema:
        """Method handle event from the client and send it to the queue.

        Args:
            event (str): Event to be handled.

        Returns:
            None: No return value.
        """

    @abstractmethod
    async def get_unfinished_films(
        self,
        pagination_params: Params,
        user_id: str,
    ) -> Page[FilmProgressResponseSchema]:
        """Method handle event from the client and send it to the queue.

        Args:
            event (str): Event to be handled.

        Returns:
            None: No return value.
        """


class FilmProgressService(IFilmProgressService):
    FILM_PROGRESS_NAMESPACE = "film_progress"

    def __init__(self, message_queue: IMessageQueue, repository: IRepository):
        self.message_queue = message_queue
        self.repository = repository

    async def create_film_progress(
        self, create_request_body: FilmProgressCreateRequestSchema, user_id: str
    ) -> FilmProgressCreateResponseSchema:
        key = build_key(film_id=create_request_body.film_id, user_id=user_id)
        film_progress_record = FilmProgressCreateResponseSchema.from_input_schema(
            create_request_body, user_id
        )

        _, entity_id = await asyncio.gather(
            self.message_queue.push(
                self.FILM_PROGRESS_NAMESPACE,
                film_progress_record.json(exclude_none=True).encode(),
                key=key.encode(),
            ),
            self.repository.insert(
                film_progress_record.dict(exclude_none=True),
                collection=self.FILM_PROGRESS_NAMESPACE,
            ),
        )

        stored_instance = await self.repository.get_by_id(
            str(entity_id),
            collection=self.FILM_PROGRESS_NAMESPACE,
        )
        return FilmProgressCreateResponseSchema(**stored_instance)

    async def get_unfinished_films(
        self,
        pagination_params: Params,
        user_id: str,
    ) -> Page[FilmProgressResponseSchema]:
        skip = (pagination_params.page - 1) * pagination_params.size

        films, total = await asyncio.gather(
            self.repository.get_list(
                collection=self.FILM_PROGRESS_NAMESPACE,
                skip=skip,
                limit=pagination_params.size,
                filters={"user_id": user_id},
            ),
            self.repository.count(
                collection=self.FILM_PROGRESS_NAMESPACE,
                filters={"user_id": user_id},
            ),
        )
        return Page.create(items=films, params=pagination_params, total=total)


def get_service(
    message_queue: MessageQueueType, repository: RepositoryType
) -> IFilmProgressService:
    return FilmProgressService(message_queue, repository)
