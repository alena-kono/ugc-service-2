from abc import ABC, abstractmethod

from motor.core import AgnosticClient
from pymongo.collection import InsertOneResult, ObjectId


class IRepository(ABC):
    @abstractmethod
    async def insert(self, data: dict, collection: str) -> ObjectId:
        """create a new record in the repository

        Args:
            data (str): Data to be pushed to the tail of the list.

        Returns:
            None: No return value.
        """

    @abstractmethod
    async def update(
        self, filters: dict[str, str], data: dict, collection: str, upsert: bool = True
    ) -> None:
        """update a record in the repository

        Args:
            entity_id (str): Entity id.
            data (str): Data to be pushed to the tail of the list.

        Returns:
            None: No return value.
        """

    @abstractmethod
    async def get_by_id(self, entity_id: str, collection: str) -> dict:
        """get a record by id from the repository

        Args:
            entity_id (str): Entity id.
            collection (str): Collection name.

        Returns:
            dict: Record.
        """

    @abstractmethod
    async def get_list(
        self,
        collection: str,
        filters: dict[str, str],
        skip: int = 0,
        limit: int | None = None,
    ) -> list[dict]:
        """get a list of records from the repository

        Args:
            collection (str): Collection name.
            limit (int): Limit of records to be returned.
            filters (dict[str:str]): Filters to be applied to the query.

        Returns:
            list[dict]: List of records.
        """

    @abstractmethod
    async def count(self, collection: str, filters: dict[str, str]) -> int:
        """count records in the repository

        Args:
            collection (str): Collection name.
            filters (dict[str:str]): Filters to be applied to the query.

        Returns:
            int: Count of records.
        """

    @abstractmethod
    async def aggregate(
        self, collection: str, filters: list[dict], limit: int | None = None
    ) -> list[dict]:
        """aggregate records in the repository

        Args:
            collection (str): Collection name.
            filters (dict[str:str]): Filters to be applied to the query.

        Returns:
            int: Count of records.
        """


class MongoRepository(IRepository):
    """MongoDB implementation."""

    def __init__(self, mongo_client: AgnosticClient, db_name: str):
        self.client = mongo_client
        self.db_name = db_name

    async def insert(self, data: dict, collection: str) -> ObjectId:
        cursor: InsertOneResult = await self.client[self.db_name][
            collection
        ].insert_one(data)
        return cursor.inserted_id

    async def update(
        self, filters: dict[str, str], data: dict, collection: str, upsert: bool = True
    ) -> None:
        await self.client[self.db_name][collection].update_one(
            filters, {"$set": data}, upsert=upsert
        )

    async def get_by_id(self, entity_id: str, collection: str) -> dict:
        cursor = await self.client[self.db_name][collection].find_one(
            {"_id": ObjectId(entity_id)}
        )  # type: ignore

        if cursor is None:
            raise ValueError(f"there is not a document with an id {entity_id}")

        return cursor

    async def get_list(
        self,
        collection: str,
        filters: dict[str, str],
        skip: int = 0,
        limit: int | None = None,
    ) -> list[dict]:
        cursor = self.client[self.db_name][collection].find(filters)
        return await cursor.skip(skip).to_list(length=limit)  # type: ignore

    async def count(self, collection: str, filters: dict[str, str]) -> int:
        return await self.client[self.db_name][collection].count_documents(filters)

    async def aggregate(
        self, collection: str, filters: list[dict], limit: int | None = None
    ) -> list[dict]:
        cursor = self.client[self.db_name][collection].aggregate(pipeline=filters)
        return await cursor.to_list(length=limit)  # type: ignore
