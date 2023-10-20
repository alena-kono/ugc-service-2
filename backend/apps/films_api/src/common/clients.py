from typing import AsyncGenerator

from aiohttp import ClientSession


async def get_http_session() -> AsyncGenerator[ClientSession, None]:
    session = ClientSession()
    yield session
    await session.close()
