from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.settings.app import get_app_settings

settings = get_app_settings()


@asynccontextmanager
async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(
        settings.postgres.dsn,
        echo=settings.service.debug,
        future=True,
    )
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as db:
        yield db
