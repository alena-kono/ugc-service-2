import logging
from contextlib import asynccontextmanager
from typing import Awaitable, Callable

import uvicorn
from aiokafka import AIOKafkaProducer
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse, Response
from fastapi_limiter import FastAPILimiter
from fastapi_pagination import add_pagination
from motor.motor_asyncio import AsyncIOMotorClient
from opentelemetry import trace
from redis import asyncio as aioredis
from starlette.middleware.sessions import SessionMiddleware

from src.common import databases
from src.film_progress.api.v1.routers import router as film_progress_router
from src.likes.api.v1.routers import router as likes_router
from src.settings.app import get_app_settings
from src.tracer.config import configure_tracer

settings = get_app_settings()
logging.config.dictConfig(settings.logging.config)


@asynccontextmanager
async def lifespan(app: FastAPI):
    databases.redis = aioredis.from_url(settings.redis.dsn, encoding="utf-8")
    databases.producer = AIOKafkaProducer(
        bootstrap_servers=settings.kafka.dsn,
        compression_type="gzip",
        enable_idempotence=True,
        max_batch_size=32768,
        linger_ms=1000,
        request_timeout_ms=10000,
        retry_backoff_ms=1000,
    )
    databases.mongodb = AsyncIOMotorClient(settings.mongo.dsn)

    await databases.producer.start()
    await FastAPILimiter.init(databases.redis)

    yield

    await databases.mongodb.close()
    await databases.redis.close()
    await databases.producer.stop()


app = FastAPI(
    lifespan=lifespan,
    title=settings.service.name,
    description=settings.service.description,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    version="0.1.0",
)


@app.get("/ping")
def pong() -> dict[str, str]:
    return {"ping": "pong!"}


@app.middleware("http")
async def check_request_id(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
):
    if not settings.service.debug:
        request_id = request.headers.get("X-Request-Id")
        if not request_id:
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "X-Request-Id is required"},
            )
    return await call_next(request)


@app.middleware("http")
async def setup_request_id_for_jaeger(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
):
    request_id = request.headers.get("X-Request-Id")
    if settings.jaeger.enabled and request_id is not None:
        tracer = trace.get_tracer(__name__)
        span = tracer.start_span("request")
        span.set_attribute("http.request_id", request_id)
        span.end()
    return await call_next(request)


app.include_router(film_progress_router, prefix="/api/v1", tags=["film_progress"])
app.include_router(likes_router, prefix="/api/v1", tags=["likes"])

app.add_middleware(SessionMiddleware, secret_key=settings.auth.secret_key)

if settings.jaeger.enabled:
    configure_tracer(app)

add_pagination(app)

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.service.host,
        port=settings.service.port,
        log_config=settings.logging.config,
        reload=settings.service.debug,
    )
