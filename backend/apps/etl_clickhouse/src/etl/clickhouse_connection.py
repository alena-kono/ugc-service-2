import logging
from contextlib import asynccontextmanager

from asynch import create_pool
from asynch.connection import Connection
from asynch.pool import Pool
from src.settings.clickhouse import ClickhouseSettings

logger = logging.getLogger(__name__)


connection_pool: Pool | None = None


@asynccontextmanager
async def create_connection_pool(clickhouse_settings: ClickhouseSettings) -> Pool:
    logger.debug("Creating clickhouse connection pool")
    async with create_pool(
        host=clickhouse_settings.host,
        port=clickhouse_settings.port,
        database=clickhouse_settings.database,
        user=clickhouse_settings.user,
        password=clickhouse_settings.password,
    ) as pool:
        yield pool


@asynccontextmanager
async def clickhouse_connection() -> Connection:
    logger.debug("Acquiring clickhouse connection")

    global connection_pool

    if not connection_pool:
        raise RuntimeError("Connection pool was not initialized")

    async with connection_pool.acquire() as connection:
        yield connection
