import pydantic
from src.settings.base import BaseAppSettings


class AuthSettings(BaseAppSettings):
    url: str = pydantic.Field(env="AUTH_URL")
    jwt_encoding_algorithm: str = pydantic.Field(
        env="AUTH_JWT_ENCODING_ALGORITHM",
        default="HS256",
    )
    jwt_secret_key: str = pydantic.Field(env="AUTH_JWT_SECRET_KEY")
    request_timeout_sec: int = pydantic.Field(env="AUTH_REQUEST_TIMEOUT_SEC", default=5)
