import pydantic
from src.settings.base import BaseAppSettings


class _GoogleSocialSettings(BaseAppSettings):
    client_id: str = pydantic.Field(env="SOCIAL_GOOGLE_CLIENT_ID")
    client_secret: str = pydantic.Field(env="SOCIAL_GOOGLE_CLIENT_SECRET")
    metadata_url: str = pydantic.Field(
        env="SOCIAL_GOOGLE_METADATA_URL",
        default="https://accounts.google.com/.well-known/openid-configuration",
    )


class _YandexSocialSettings(BaseAppSettings):
    client_id: str = pydantic.Field(env="SOCIAL_YANDEX_CLIENT_ID")
    client_secret: str = pydantic.Field(env="SOCIAL_YANDEX_CLIENT_SECRET")
    authorize_url: str = pydantic.Field(
        env="SOCIAL_YANDEX_AUTHORIZE_URL",
        default="https://oauth.yandex.ru/authorize",
    )
    access_token_url: str = pydantic.Field(
        env="SOCIAL_YANDEX_ACCESS_TOKEN_URL",
        default="https://oauth.yandex.ru/token",
    )
    userinfo_endpoint: str = pydantic.Field(
        env="SOCIAL_YANDEX_USERINFO_ENDPOINT",
        default="https://login.yandex.ru/info",
    )


class SocialSettings(BaseAppSettings):
    google = _GoogleSocialSettings()
    yandex = _YandexSocialSettings()
