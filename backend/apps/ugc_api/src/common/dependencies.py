from typing import Annotated

from aiokafka import AIOKafkaProducer
from fastapi import Depends
from fastapi_limiter.depends import RateLimiter
from motor.core import AgnosticClient
from src.common.authorization import JWTBearer, JwtClaims
from src.common.databases import get_kafka_producer, get_mongodb
from src.common.message_queue import IMessageQueue, KafkaMessageQueue
from src.common.repositories import IRepository, MongoRepository
from src.settings.app import get_app_settings

settings = get_app_settings()

KafkaProducerType = Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]
MongoCLientType = Annotated[AgnosticClient, Depends(get_mongodb)]


def get_message_queue(kafka_producer: KafkaProducerType) -> IMessageQueue:
    return KafkaMessageQueue(kafka_producer=kafka_producer)


def get_repository(mongo_client: MongoCLientType) -> IRepository:
    return MongoRepository(mongo_client=mongo_client, db_name=settings.mongo.db_name)


UserToken = Annotated[JwtClaims, Depends(JWTBearer())]
MessageQueueType = Annotated[IMessageQueue, Depends(get_message_queue)]
RepositoryType = Annotated[IRepository, Depends(get_repository)]
RateLimiterType = Annotated[
    RateLimiter,
    Depends(
        RateLimiter(
            times=settings.rate_limiter.STANDARD_LIMIT.times,
            seconds=settings.rate_limiter.STANDARD_LIMIT.seconds,
        )
    ),
]
