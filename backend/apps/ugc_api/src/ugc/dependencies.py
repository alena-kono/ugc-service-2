from typing import Annotated
from motor.core import AgnosticClient
from fastapi import Depends
from fastapi_limiter.depends import RateLimiter
from src.settings.app import get_app_settings
from src.utils.authorization import JWTBearer, JwtClaims
from src.utils.databases import get_kafka_producer, get_mongodb
from src.ugc.message_queue import IMessageQueue, KafkaMessageQueue
from src.ugc.services import EventService, IEventService
from src.ugc.repositories import IRepository, MongoRepository

from aiokafka import AIOKafkaProducer

settings = get_app_settings()

KafkaProducerType = Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]
MongoCLientType = Annotated[AgnosticClient, Depends(get_mongodb)]


def get_message_queue(kafka_producer: KafkaProducerType) -> IMessageQueue:
    return KafkaMessageQueue(kafka_producer=kafka_producer)


def get_repository(mongo_client: MongoCLientType) -> IRepository:
    return MongoRepository(mongo_client=mongo_client, db_name=settings.mongo.db_name)


MessageQueueType = Annotated[IMessageQueue, Depends(get_message_queue)]
RepositoryType = Annotated[IRepository, Depends(get_repository)]


def get_event_service(
    queue_repository: MessageQueueType, repository: RepositoryType
) -> IEventService:
    return EventService(message_queue=queue_repository, repository=repository)


EventServiceType = Annotated[IEventService, Depends(get_event_service)]

RateLimiterType = Annotated[
    RateLimiter,
    Depends(
        RateLimiter(
            times=settings.rate_limiter.STANDARD_LIMIT.times,
            seconds=settings.rate_limiter.STANDARD_LIMIT.seconds,
        )
    ),
]

UserToken = Annotated[JwtClaims, Depends(JWTBearer())]
