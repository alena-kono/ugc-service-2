from typing import Annotated

from fastapi import Depends
from fastapi_limiter.depends import RateLimiter
from src.settings.app import get_app_settings
from src.ugc.authorization import JWTBearer
from src.ugc.database import get_kafka_producer
from src.ugc.message_queue import IMessageQueue, KafkaMessageQueue
from src.ugc.schemas import JwtClaims
from src.ugc.services import EventService, IEventService

from aiokafka import AIOKafkaProducer

settings = get_app_settings()

KafkaProducerType = Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]


def get_queue_repository(kafka_producer: KafkaProducerType) -> IMessageQueue:
    return KafkaMessageQueue(kafka_producer=kafka_producer)


MessageQueueType = Annotated[IMessageQueue, Depends(get_queue_repository)]


def get_event_service(queue_repository: MessageQueueType) -> IEventService:
    return EventService(message_queue=queue_repository)


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
