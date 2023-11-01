from collections.abc import Callable
from typing import Any

import orjson
from pydantic import BaseModel


def orjson_dumps(value: dict[str, Any], *, default: Any) -> str:
    return orjson.dumps(value, default=default).decode()


class AppBaseSchema(BaseModel):
    class Config:
        orm_mode: bool = True
        json_loads: Callable = orjson.loads
        json_dumps: Callable = orjson_dumps
