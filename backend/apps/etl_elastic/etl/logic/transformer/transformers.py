from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Type, cast

from etl.logic.storage.storage import Storage

from .dataclasses import SQLContainer


class TransformerInt(ABC):
    dataclass: Type[SQLContainer]

    input_topic: str
    output_topic: str

    storage: Storage

    @abstractmethod
    def transform(self) -> None:
        ...


class BaseTrasformer(TransformerInt):
    dataclass = SQLContainer
    storage = Storage()

    def transform(self) -> None:
        sql_data = self.storage.get(self.input_topic)
        if not sql_data:
            return
        es_data = self.dataclass(batch=sql_data.pop())
        self.storage.set_value(self.output_topic, es_data.transform())


class MoviesTransformer(BaseTrasformer):
    input_topic = "movies_sql_data"
    output_topic = "movies_es_data"


class GenreTransformer(BaseTrasformer):
    input_topic = "genres_sql_data"
    output_topic = "genres_es_data"


class PersonTransformer(BaseTrasformer):
    input_topic = "persons_sql_data"
    output_topic = "persons_es_data"


@lru_cache
def get_transformers() -> list[TransformerInt]:
    mergers = [merger() for merger in BaseTrasformer.__subclasses__()]
    return cast(list[TransformerInt], mergers)


def run_transformers() -> None:
    for transformer in get_transformers():
        transformer.transform()
