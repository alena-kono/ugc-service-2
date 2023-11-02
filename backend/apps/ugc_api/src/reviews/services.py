import asyncio
from abc import ABC, abstractmethod

from fastapi_pagination import Page, Params
from pymongo.collection import ObjectId
from src.common.dependencies import MessageQueueType, RepositoryType
from src.common.message_queue import IMessageQueue, build_key
from src.common.repositories import IRepository
from src.reviews.schemas import (
    ReviewCreateRequestSchema,
    ReviewCreateResponseSchema,
    ReviewResponseSchema,
    ReviewUpdateRequestSchema,
    ReviewUpdateResponseSchema,
)


class IReviewService(ABC):
    @abstractmethod
    async def create_review_record(
        self, create_request_body: ReviewCreateRequestSchema, user_id: str
    ) -> ReviewCreateResponseSchema:
        """Method handle event from the client and send it to the queue.

        Args:
           create_request_body (ReviewCreateRequestSchema): Event to be handled.

        Returns:
            None: No return value.
        """

    @abstractmethod
    async def update_review_record(
        self,
        update_request_body: ReviewUpdateRequestSchema,
        user_id: str,
        review_id: str,
    ) -> ReviewUpdateResponseSchema:
        """Method handle event from the client and send it to the queue.

        Args:
            update_request_body (ReviewUpdateRequestSchema): Event to be handled.
            user_id (str): user id .
            review_id (str): review id .

        Returns:
            None: No return value.
        """

    @abstractmethod
    async def get_user_review(self, film_id: str, user_id: str) -> ReviewResponseSchema:
        """Method handle event from the client and send it to the queue.

        Args:
            film_id (str): film id related to requested reviews.
            user_id (str): user id .

        Returns:
            None: No return value.
        """

    @abstractmethod
    async def get_films_reviews(
        self,
        film_id: str,
        pagination_params: Params,
    ) -> Page[ReviewResponseSchema]:
        """Method handle event from the client and send it to the queue.

        Args:
            film_id (str): film id of related to reviews .

        Returns:
            None: No return value.
        """


class ReviewService(IReviewService):
    REVIEWS_NAMESPACE = "reviews"

    def __init__(self, message_queue: IMessageQueue, repository: IRepository):
        self.message_queue = message_queue
        self.repository = repository

    async def create_review_record(
        self, create_request_body: ReviewCreateRequestSchema, user_id: str
    ) -> ReviewCreateResponseSchema:
        key = build_key(film_id=create_request_body.film_id, user_id=user_id)
        review_record = ReviewCreateResponseSchema.from_input_schema(
            create_request_body, user_id
        )

        _, inserted_id = await asyncio.gather(
            self.message_queue.push(
                self.REVIEWS_NAMESPACE,
                review_record.json(exclude_none=True).encode(),
                key=key.encode(),
            ),
            self.repository.insert(
                data=review_record.dict(exclude_none=True),
                collection=self.REVIEWS_NAMESPACE,
            ),
        )

        stored_instance = await self.repository.get_by_id(
            entity_id=str(inserted_id),
            collection=self.REVIEWS_NAMESPACE,
        )
        return ReviewCreateResponseSchema(**stored_instance)

    async def update_review_record(
        self,
        update_request_body: ReviewUpdateRequestSchema,
        user_id: str,
        review_id: str,
    ) -> ReviewUpdateResponseSchema:
        key = build_key(film_id=update_request_body.film_id, user_id=user_id)
        review_record = ReviewUpdateResponseSchema.from_input_schema(
            update_request_body, user_id
        )
        await asyncio.gather(
            self.message_queue.push(
                self.REVIEWS_NAMESPACE,
                review_record.json(exclude_none=True).encode(),
                key=key.encode(),
            ),
            self.repository.update(
                filters={"_id": str(ObjectId(review_id))},
                data=review_record.dict(exclude_none=True),
                collection=self.REVIEWS_NAMESPACE,
                upsert=False,
            ),
        )

        updated_review = await self.repository.get_by_id(
            entity_id=review_id,
            collection=self.REVIEWS_NAMESPACE,
        )

        return ReviewUpdateResponseSchema(**updated_review)

    async def get_user_review(self, film_id: str, user_id: str) -> ReviewResponseSchema:
        review, *_ = await self.repository.get_list(
            collection=self.REVIEWS_NAMESPACE,
            limit=1,
            filters={"film_id": film_id, "user_id": user_id},
        )
        # * review is a list of dicts, so we need to get the first element
        # * because we expect only one review per user per film
        return ReviewResponseSchema(**review)

    async def get_films_reviews(
        self,
        film_id: str,
        pagination_params: Params,
    ) -> Page[ReviewResponseSchema]:
        skip = (pagination_params.page - 1) * pagination_params.size

        reviews, total = await asyncio.gather(
            self.repository.get_list(
                collection=self.REVIEWS_NAMESPACE,
                skip=skip,
                limit=pagination_params.size,
                filters={"film_id": film_id},
            ),
            self.repository.count(
                collection=self.REVIEWS_NAMESPACE,
                filters={"film_id": film_id},
            ),
        )
        return Page.create(items=reviews, params=pagination_params, total=total)


def get_service(
    message_queue: MessageQueueType, repository: RepositoryType
) -> IReviewService:
    return ReviewService(message_queue, repository)
