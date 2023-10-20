from typing import AsyncGenerator

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from src.settings.app import AppSettings


class Base(AsyncAttrs, DeclarativeBase):
    ...


async_session: async_sessionmaker | None
engine: None | AsyncEngine = None
redis: None | Redis = None


def init_database(settings: AppSettings) -> None:
    global engine
    global async_session

    engine = create_async_engine(
        settings.postgres.dsn,
        echo=settings.service.debug,
        future=True,
    )
    async_session = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )


async def create_database() -> None:
    if engine is None:
        raise RuntimeError("Engine has not been defined.")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def purge_database() -> None:
    if engine is None:
        raise RuntimeError("Engine has not been defined.")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def get_db() -> AsyncGenerator[None, AsyncSession]:
    global async_session

    if async_session is None:
        raise RuntimeError("SQL client has not been defined.")

    async with async_session() as db:
        yield db


async def get_redis() -> Redis:
    if redis is None:
        raise RuntimeError("Redis client has not been defined.")

    return redis
