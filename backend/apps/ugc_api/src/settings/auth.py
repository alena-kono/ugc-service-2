import pydantic
from src.settings.base import BaseAppSettings


class AuthSettings(BaseAppSettings):
    secret_key: str = pydantic.Field(env="SECRET_KEY")
    jwt_encoding_algorithm: str = pydantic.Field(
        env="AUTH_JWT_ENCODING_ALGORITHM",
        default="HS256",
    )
    jwt_secret_key: str = pydantic.Field(env="AUTH_JWT_SECRET_KEY")

    access_token_expires_secs: int = pydantic.Field(
        env="AUTH_ACCESS_TOKEN_EXPIRES_SECS"
    )
    refresh_token_expires_secs: int = pydantic.Field(
        env="AUTH_REFRESH_TOKEN_EXPIRES_SECS"
    )
