from collections import defaultdict
from typing import Any


class Storage:
    storage: dict[str, list] = defaultdict(list)

    @classmethod
    def get(cls, key: str) -> list:
        return cls.storage[key]

    @classmethod
    def set_value(cls, key: str, value: Any) -> None:
        cls.storage[key].append(value)

    @classmethod
    def clean(cls) -> None:
        cls.storage = defaultdict(list)
