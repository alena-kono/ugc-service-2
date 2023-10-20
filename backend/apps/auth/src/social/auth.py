"""Social authorization module.

Contains implementations of social providers authorization backends.
"""
from abc import ABC, abstractmethod
from typing import Annotated, Any

from fastapi import Depends, Request
from src.settings.app import get_app_settings
from src.social import client as social_client
from src.social.client import IOAuthClient, OAuthAppClient
from src.social.exceptions import SocialProviderUnknownError
from src.social.providers import SocialProviderSlug
from src.social.schemas import UserSocial

settings = get_app_settings()


class ISocialAuthBackend(ABC):
    """Social authorization interface."""

    provider_slug: str
    oauth_client: IOAuthClient

    @abstractmethod
    async def authorize_url(self, auth_url: str, request: Request) -> str | None:
        """Authorize URL for redirect."""
        ...

    @abstractmethod
    async def get_user_info(
        self, token_decoded: dict[str, Any], request: Request
    ) -> UserSocial:
        """Get user info from social provider."""
        ...

    @abstractmethod
    async def get_access_token(self, request: Request) -> dict[str, Any]:
        """Authorize access token."""
        ...


class BaseSocialAuthBackend(ISocialAuthBackend):
    def __init__(self, oauth_client: IOAuthClient, provider_slug: str) -> None:
        self.oauth_client = oauth_client
        self.provider_slug = provider_slug

    @abstractmethod
    async def authorize_url(self, auth_url: str, request: Request) -> str | None:
        raise NotImplementedError

    @abstractmethod
    async def get_user_info(
        self, token_decoded: dict[str, Any], request: Request
    ) -> UserSocial:
        raise NotImplementedError

    async def get_access_token(self, request: Request) -> dict[str, Any]:
        return await self.oauth_client.get_access_token(request=request)


class GoogleSocialAuthBackend(BaseSocialAuthBackend):
    """Google social authorization."""

    async def authorize_url(
        self, auth_url: str, request: Request, **options
    ) -> str | None:
        url_data = await self.oauth_client.create_authorization_url(
            auth_url,
            **options,
        )
        await self.oauth_client.save_authorize_data(
            redirect_uri=auth_url,
            request=request,
            **url_data,
        )
        return url_data.get("url")

    async def get_user_info(
        self, token_decoded: dict[str, Any], request: Request
    ) -> UserSocial | None:
        if user_info := await self.oauth_client.get_user_info(
            token=token_decoded, request=request
        ):
            return await self._prepare_user_info(user_info)

        return None

    async def _prepare_user_info(self, user_info: dict[str, Any]) -> UserSocial:
        return UserSocial(
            social_id=user_info.get("sub"),
            email=user_info.get("email"),
            provider_slug=self.provider_slug,
        )


class YandexSocialAuthBackend(BaseSocialAuthBackend):
    """Yandex social authorization."""

    async def authorize_url(self, request: Request, auth_url: str) -> str:
        url_data = await self.oauth_client.create_authorization_url(auth_url)
        await self.oauth_client.save_authorize_data(
            redirect_uri=auth_url, request=request, **url_data
        )
        return url_data.get("url")

    async def get_user_info(
        self, token_decoded: dict[str, Any], request: Request
    ) -> UserSocial | None:
        if user_info := await self.oauth_client.get_user_info(
            token=token_decoded, request=request
        ):
            return await self._prepare_user_info(user_info)

        return None

    async def _prepare_user_info(self, user_info: dict) -> UserSocial:
        prepared_user_info = {
            "social_id": user_info.get("id"),
            "email": user_info.get("default_email"),
            "provider_slug": self.provider_slug,
        }
        return UserSocial(**prepared_user_info)


async def get_social_auth_backend(
    provider_slug: SocialProviderSlug,
    oauth_client: Annotated[
        OAuthAppClient, Depends(social_client.get_registered_oauth_client)
    ],
) -> ISocialAuthBackend:
    """Get appropriate authorization service by provider slug.

    Use authlib OAuth client.
    """
    oauth_client.init_app(app_name=provider_slug.value)

    match provider_slug:  # noqa: E999
        case SocialProviderSlug.GOOGLE:
            return GoogleSocialAuthBackend(
                oauth_client=oauth_client, provider_slug=provider_slug.value
            )

        case SocialProviderSlug.YANDEX:
            return YandexSocialAuthBackend(
                oauth_client=oauth_client, provider_slug=provider_slug.value
            )

    raise SocialProviderUnknownError
