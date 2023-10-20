from abc import ABC, abstractmethod

from authlib.integrations.starlette_client import OAuth as OAuthStarletteClient
from authlib.integrations.starlette_client import StarletteOAuth1App, StarletteOAuth2App
from src.settings.app import get_app_settings
from src.social.exceptions import SocialProviderNotRegisteredError
from src.social.providers import SocialProviderSlug

settings = get_app_settings()


class IOAuthClient(ABC):
    """OAuth client interface."""

    @abstractmethod
    def __init__(self, client: OAuthStarletteClient):
        ...

    @abstractmethod
    def register(self, **kwargs) -> None:
        ...

    @abstractmethod
    async def create_authorization_url(self, url: str, **kwargs) -> dict:
        """Build authorization url with optional parameters."""
        ...

    @abstractmethod
    async def save_authorize_data(self, **kwargs) -> None:
        """Save authorization related data to state."""
        ...

    @abstractmethod
    async def get_access_token(self, **kwargs) -> dict:
        """Receive access token from social provider."""
        ...

    @abstractmethod
    async def get_user_info(self, **kwargs) -> dict:
        """Get user info from social provider."""
        ...


class OAuthAppClient:
    """OAuth authlib based client."""

    def __init__(self, client: OAuthStarletteClient) -> None:
        self._client = client
        self.app_client: StarletteOAuth1App | StarletteOAuth2App | None = None

    def init_app(self, app_name: str) -> StarletteOAuth1App | StarletteOAuth2App:
        if app := getattr(self._client, app_name, None):
            self.app_client = app
            return app
        raise SocialProviderNotRegisteredError(
            f"Such social provider has not been registered: {app_name}"
        )

    def register(self, **kwargs) -> None:
        return self._client.register(**kwargs)

    async def create_authorization_url(self, url: str, **kwargs) -> dict:
        """Build authorization url with optional parameters."""
        return await self.app_client.create_authorization_url(url, **kwargs)

    async def save_authorize_data(self, **kwargs) -> None:
        """Save authorization related data to state."""
        return await self.app_client.save_authorize_data(**kwargs)

    async def get_access_token(self, **kwargs) -> dict:
        """Get access token from social provider."""
        return await self.app_client.authorize_access_token(**kwargs)

    async def get_user_info(self, **kwargs) -> dict:
        """Get user info from social provider."""
        return await self.app_client.userinfo(**kwargs)


async def get_registered_oauth_client() -> OAuthAppClient:
    oauth_client = OAuthAppClient(client=OAuthStarletteClient())
    oauth_client.register(
        name=SocialProviderSlug.GOOGLE.value,
        client_id=settings.social.google.client_id,
        client_secret=settings.social.google.client_secret,
        server_metadata_url=settings.social.google.metadata_url,
        client_kwargs={"scope": "openid email profile", "prompt": "select_account"},
    )
    oauth_client.register(
        name=SocialProviderSlug.YANDEX.value,
        client_id=settings.social.yandex.client_id,
        client_secret=settings.social.yandex.client_secret,
        authorize_url=settings.social.yandex.authorize_url,
        access_token_url=settings.social.yandex.access_token_url,
        userinfo_endpoint=settings.social.yandex.userinfo_endpoint,
    )
    return oauth_client
