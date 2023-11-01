import logging
from contextlib import asynccontextmanager
from typing import Awaitable, Callable

import sentry_sdk
import structlog
import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse, Response
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_limiter import FastAPILimiter
from fastapi_pagination import add_pagination
from opentelemetry import trace
from redis import asyncio as aioredis
from starlette.middleware.sessions import SessionMiddleware

from src.auth.api.v1 import router as auth_router
from src.common import database
from src.permissions.api.v1 import router as permissions_router
from src.settings.app import get_app_settings
from src.settings.logging import configure_logger
from src.social.api.v1 import router as social_router
from src.tracer.config import configure_tracer
from src.users.api.v1 import router as users_router

settings = get_app_settings()

logging.config.dictConfig(settings.logging.config)
configure_logger(enable_async_logger=False)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.redis = aioredis.from_url(settings.redis.dsn, encoding="utf-8")
    FastAPICache.init(RedisBackend(database.redis), prefix="fastapi-cache")
    await FastAPILimiter.init(database.redis)

    database.init_database(settings)

    yield
    await database.redis.close()


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
    logger.info("pong")
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
async def logging_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    structlog.contextvars.clear_contextvars()

    structlog.contextvars.bind_contextvars(
        request_id=request.headers.get("X-Request-Id"),
        service_name=settings.service.name,
    )

    response: Response = await call_next(request)

    return response


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


app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users_router.router, prefix="/api/v1/users", tags=["users"])
app.include_router(
    permissions_router.router, prefix="/api/v1/permissions", tags=["permissions"]
)
app.include_router(social_router.router, prefix="/api/v1/social", tags=["social"])

app.add_middleware(SessionMiddleware, secret_key=settings.auth.secret_key)
add_pagination(app)

if settings.jaeger.enabled:
    configure_tracer(app)

if settings.sentry.enabled:
    sentry_sdk.init(
        dsn=settings.sentry.dsn,
        enable_tracing=True,
    )

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.service.host,
        port=settings.service.port,
        reload=settings.service.debug,
    )
