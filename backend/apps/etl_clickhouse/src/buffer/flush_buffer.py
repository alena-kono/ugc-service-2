import asyncio
import logging
import sys
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from typing import Any, Self

logger = logging.getLogger()


class FlushableBuffer(ABC):
    """Interface for async buffers that can automatically flush based on different conditions"""

    def __init__(self) -> None:
        self.__buffer: list = []
        self.__data_size: int = 0
        self.__on_flush_callbacks: list[Callable] = []

    @abstractmethod
    async def _on_push(self) -> None:
        pass

    async def __on_buffer_flush(self, buffer: tuple) -> None:
        logger.debug(
            f"Processing buffer data, callbacks n = {len(self.__on_flush_callbacks)}, buffer = {self.__buffer}"
        )
        await asyncio.gather(
            *[callback(buffer) for callback in self.__on_flush_callbacks]
        )

    def add_on_flush_callback(self, callback: Callable) -> None:
        logger.debug(f"Add new on_flush_callback = {callback}")
        self.__on_flush_callbacks.append(callback)

    async def flush(self) -> None:
        logger.debug(
            f"Flushing buffer, size = {self.__data_size}, buffer = {self.__buffer}"
        )
        if not len(self.__buffer):
            return None
        buffer_copy = tuple(self.__buffer)
        self.__buffer.clear()
        self.__data_size = 0
        await self.__on_buffer_flush(buffer_copy)

    async def push(self, data: Any, size: int | None = None) -> None:
        logger.debug(f"Pushing to buffer data = {data}, size = {size}")
        self.__buffer.append(data)

        if size is None:
            self.__data_size += sys.getsizeof(data)
        else:
            self.__data_size += size

        await self._on_push()

    def buffer_data_size(self) -> int:
        return self.__data_size

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *excinfo) -> None:
        logger.debug(f"Flushing buffer on exit, buffer = {self.__buffer}")
        await self.flush()


class FlushableMemoryBuffer(FlushableBuffer):
    def __init__(self, max_buffer_bytes: int = 0) -> None:
        super().__init__()
        self._max_buffer_size = max_buffer_bytes

    async def _on_push(self) -> None:
        if self.buffer_data_size() >= self._max_buffer_size:
            logger.debug("Buffer overflows, flushing")
            await self.flush()


@asynccontextmanager
async def get_flushable_buffer(
    *, max_buffer_size: int
) -> AsyncGenerator[FlushableBuffer, None]:
    async with FlushableMemoryBuffer(max_buffer_size) as fb:
        yield fb
