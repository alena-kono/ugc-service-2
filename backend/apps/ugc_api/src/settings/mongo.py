import pydantic
from src.settings.base import BaseAppSettings


class MongoSettings(BaseAppSettings):
    host: str = pydantic.Field(env="MONGO_HOST")
    port: int = pydantic.Field(env="MONGO_PORT")
    db_name: str = pydantic.Field(env="MONGO_DB_NAME")

    @property
    def dsn(self) -> str:
        return f"{self.host}:{self.port}"
