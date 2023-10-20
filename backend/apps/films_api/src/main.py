import logging
from contextlib import asynccontextmanager
from typing import Awaitable, Callable

import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, ORJSONResponse, Response
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from opentelemetry import trace
from redis import asyncio as aioredis
from src.common import database
from src.common.exceptions import AuthIsUnavailableError
from src.common.utils import ESHandler
from src.films.api.v1 import router as films_router
from src.films.error_handling import personalized_content_graceful_degradation
from src.genres.api.v1 import router as genres_router
from src.persons.api.v1 import router as persons_routers
from src.settings.app import AppSettings
from src.tracer.config import configure_tracer

settings = AppSettings.get()
logging.config.dictConfig(settings.logging.config)


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.redis = aioredis.from_url(settings.redis.dsn, encoding="utf-8")
    FastAPICache.init(RedisBackend(database.redis), prefix="fastapi-cache")
    database.es_handler = ESHandler(client=AsyncElasticsearch(settings.elastic.dsn))
    yield
    await database.redis.close()
    await database.es_handler.close()


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
    if not settings.is_development:
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


@app.exception_handler(AuthIsUnavailableError)
async def auth_is_unavailable_error_handler(
    request: Request, exc: AuthIsUnavailableError
):
    match (request.url.path):  # noqa: E999
        case "/api/v1/films/personalized":
            return await personalized_content_graceful_degradation(request, exc)
        case _:
            return JSONResponse(
                status_code=500,
                content={"detail": "Auth is unavailable"},
            )


app.include_router(films_router.router, prefix="/api/v1/films", tags=["films"])
app.include_router(genres_router.router, prefix="/api/v1/genres", tags=["genres"])
app.include_router(persons_routers.router, prefix="/api/v1/persons", tags=["persons"])

if settings.jaeger.enabled:
    configure_tracer(app)


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.service.host,
        port=settings.service.port,
        log_config=settings.logging.config,
        reload=True,
    )
