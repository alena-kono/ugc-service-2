import asyncio
from abc import ABC, abstractmethod

from src.common.dependencies import MessageQueueType, RepositoryType
from src.common.message_queue import IMessageQueue, build_key
from src.common.repositories import IRepository
from src.likes.schemas import (
    AverageRankResponseSchema,
    LikeCreateRequestSchema,
    LikeCreateResponseSchema,
    LikeResponseSchema,
    TotalLikesResponseSchema,
)


class ILikeService(ABC):
    @abstractmethod
    async def create_like_record(
        self, create_request_body: LikeCreateRequestSchema, user_id: str
    ) -> LikeCreateResponseSchema:
        """Method handle event from the client and send it to the queue.

        Args:
            event (str): Event to be handled.

        Returns:
            None: No return value.
        """

    @abstractmethod
    async def get_total_likes(self, film_id: str) -> TotalLikesResponseSchema:
        """Method handle event from the client and send it to the queue.

        Args:
            event (str): Event to be handled.

        Returns:
            None: No return value.
        """

    @abstractmethod
    async def get_average_rank(self, film_id: str) -> AverageRankResponseSchema:
        """Method handle event from the client and send it to the queue.

        Args:
            event (str): Event to be handled.

        Returns:
            None: No return value.
        """

    @abstractmethod
    async def get_user_like(self, film_id: str, user_id: str) -> LikeResponseSchema:
        """Method handle event from the client and send it to the queue.

        Args:
            event (str): Event to be handled.

        Returns:
            None: No return value.
        """


class LikeService(ILikeService):
    LIKES_NAMESPACE = "likes"

    def __init__(self, message_queue: IMessageQueue, repository: IRepository):
        self.message_queue = message_queue
        self.repository = repository

    async def create_like_record(
        self, create_request_body: LikeCreateRequestSchema, user_id: str
    ) -> LikeCreateResponseSchema:
        key = build_key(film_id=create_request_body.film_id, user_id=user_id)
        like_record = LikeCreateResponseSchema.from_input_schema(
            create_request_body, user_id
        )

        filters = {"film_id": create_request_body.film_id, "user_id": user_id}
        await asyncio.gather(
            self.message_queue.push(
                self.LIKES_NAMESPACE,
                like_record.json(exclude_none=True).encode(),
                key=key.encode(),
            ),
            self.repository.update(
                filters=filters,
                data=like_record.dict(exclude_none=True),
                collection=self.LIKES_NAMESPACE,
            ),
        )

        stored_instance, *_ = await self.repository.get_list(
            filters=filters,
            limit=1,
            collection=self.LIKES_NAMESPACE,
        )
        return LikeCreateResponseSchema(**stored_instance)

    async def get_total_likes(self, film_id: str) -> TotalLikesResponseSchema:
        total_likes = await self.repository.count(
            collection=self.LIKES_NAMESPACE,
            filters={"film_id": film_id},
        )

        return TotalLikesResponseSchema(total_likes=total_likes, film_id=film_id)

    async def get_average_rank(self, film_id: str) -> AverageRankResponseSchema:
        pipeline: list[dict] = [
            {"$match": {"film_id": film_id}},
            {"$group": {"_id": "$film_id", "average_rank": {"$avg": "$rank"}}},
        ]

        average_film_rank, *_ = await self.repository.aggregate(
            collection=self.LIKES_NAMESPACE,
            filters=pipeline,
        )

        return AverageRankResponseSchema(**{**average_film_rank, "film_id": film_id})

    async def get_user_like(self, film_id: str, user_id: str) -> LikeResponseSchema:
        like, *_ = await self.repository.get_list(
            collection=self.LIKES_NAMESPACE,
            limit=1,
            filters={"film_id": film_id, "user_id": user_id},
        )
        # * like is a list of dicts, so we need to get the first element
        # * because we expect only one like per user per film
        return LikeResponseSchema(**like)


def get_service(
    message_queue: MessageQueueType, repository: RepositoryType
) -> ILikeService:
    return LikeService(message_queue, repository)
