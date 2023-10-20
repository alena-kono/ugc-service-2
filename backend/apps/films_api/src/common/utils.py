import logging
from typing import Any, AsyncGenerator, Sequence, Type, TypeVar

from elasticsearch import AsyncElasticsearch, NotFoundError, RequestError
from elasticsearch.helpers import async_scan
from src.common.exceptions import ElasticsearchRepositoryError
from src.common.models import AppBaseModel
from src.common.schemas import AppBaseSchema

logger = logging.getLogger(__name__)

SchemaType = TypeVar("SchemaType", bound=AppBaseSchema, covariant=True)


class ESHandler:
    def __init__(self, client: AsyncElasticsearch) -> None:
        self.client = client

    async def get(
        self, index: str, query: dict[str, Any]
    ) -> list[dict[str, Any]] | None:
        try:
            docs = await self.client.search(
                index=index,
                body=query,
            )
        except NotFoundError:
            return None
        except RequestError as err:
            logger.error(err)
            raise ElasticsearchRepositoryError from err

        return [doc["_source"] for doc in docs["hits"]["hits"]]

    async def get_by_id(
        self,
        index: str,
        item_id: str,
    ) -> dict[str, Any] | None:
        try:
            doc = await self.client.get(index=index, id=item_id)
        except NotFoundError:
            return None
        except RequestError as err:
            logger.error(err)
            raise ElasticsearchRepositoryError from err
        return doc["_source"]

    async def scan(
        self, index: str, query: dict[str, Any]
    ) -> AsyncGenerator[dict[str, Any], None]:
        async for doc in async_scan(client=self.client, query=query, index=index):
            yield doc["_source"]

    def get_client(self) -> AsyncElasticsearch:
        return self.client

    async def close(self) -> None:
        await self.client.close()


def models_to_schemas(
    models: Sequence[AppBaseModel] | None, schema_type: Type[SchemaType]
) -> list[SchemaType]:
    if not models:
        return []
    return [schema_type.from_model(model) for model in models]
