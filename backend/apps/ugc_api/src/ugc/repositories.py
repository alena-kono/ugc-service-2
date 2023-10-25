from abc import ABC, abstractmethod
from motor.core import AgnosticClient
from pymongo.results import InsertOneResult


class IRepository(ABC):
    @abstractmethod
    async def insert(self, data: dict, collection: str) -> dict:
        """create a new record in the repository

        Args:
            data (str): Data to be pushed to the tail of the list.

        Returns:
            None: No return value.
        """

    @abstractmethod
    async def get_by_id(self, entity_id: str, collection: str) -> dict:
        ...


class MongoRepository(IRepository):
    """MongoDB implementation."""

    def __init__(self, mongo_client: AgnosticClient, db_name: str):
        self.client = mongo_client
        self.db_name = db_name

    async def insert(self, data: dict, collection: str) -> InsertOneResult:
        cursor: InsertOneResult = await self.client[self.db_name][collection].insert_one(data)
        return cursor.inserted_id

    async def get_by_id(self, entity_id: str, collection: str) -> dict:
        cursor = await self.client[self.db_name][collection].find_one({"_id": entity_id})

        if cursor is None:
            raise ValueError(f"there is not a document with an id {entity_id}")
            
        return cursor
