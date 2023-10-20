import logging
from abc import ABC, abstractmethod
from typing import Annotated
from uuid import UUID

import sqlalchemy.exc as sqlalchemy_exc
from authlib.integrations.base_client import MismatchingStateError, MissingTokenError
from fastapi import Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth import dependencies as auth_depends
from src.auth.jwt import schemas as jwt_schemas
from src.common.database import get_db
from src.social import auth as social_auth
from src.social import client as social_client
from src.social import schemas as social_schemas
from src.social.exceptions import (
    InvalidSocialProviderAccessTokenError,
    SocialAccountAlreadyExistsError,
    SocialServiceError,
    UserSocialInfoParseError,
)
from src.social.repositories import (
    PostgresSocialAccountRepository,
    SocialAccountRepository,
)
from src.users import dependencies as user_depends
from src.users.service import UserService

logger = logging.getLogger(__name__)


class ISocialAccountService(ABC):
    @abstractmethod
    async def sign_in_with_social_provider_account(
        self, request: Request, fingerprint: auth_depends.UserFingerprint
    ) -> social_schemas.SocialAccount:
        ...

    @abstractmethod
    async def redirect_to_social_provider(
        self, target_auth_url: str, request: Request
    ) -> RedirectResponse:
        ...


class SocialAccountService(ISocialAccountService):
    def __init__(
        self,
        social_auth_backend: Annotated[
            social_auth.ISocialAuthBackend,
            Depends(social_client.get_registered_oauth_client),
        ],
        social_account_repo: SocialAccountRepository,
        user_service: UserService,
    ) -> None:
        self.social_auth_backend = social_auth_backend
        self.social_account_repo = social_account_repo
        self.user_service = user_service

    async def sign_in_with_social_provider_account(
        self, request: Request, fingerprint: auth_depends.UserFingerprint
    ) -> jwt_schemas.JWTCredentials:
        """Sign in user using their social account.

        Retrieve user info from decoded token.
        Create User and SocialAccount in the database if they do not exist,
        otherwise get them.
        Generate JWT credentials for the User.

        Args:
            request (Request): Request object.
            fingerprint (auth_depends.UserFingerprint): User fingerprint.

        Raises:
            InvalidSocialProviderAccessTokenError: Token is invalid or
                has mismatching state.
            UserSocialInfoParseError: User info cannot be parsed from social provider.

        Returns:
            jwt_schemas.JWTCredentials: JWT credentials.
        """
        logger.debug("SocialAccountService:sign_in_with_social_provider_account")
        try:
            token_decoded = await self.social_auth_backend.get_access_token(
                request=request
            )
        except (MismatchingStateError, MissingTokenError) as err:
            logger.debug("Token is invalid or has mismatching state")
            raise InvalidSocialProviderAccessTokenError from err

        logger.debug(f"{token_decoded=}")

        if user_info := await self.social_auth_backend.get_user_info(
            token_decoded=token_decoded,
            request=request,
        ):
            user = await self.user_service.get_by_username(username=user_info.email)
            if not user:
                # Generate a random password, so user could change it in the future
                user = await self.user_service.create_user(
                    username=user_info.email,
                    password=await self.user_service.generate_random_password(),
                    first_name="",
                    last_name="",
                )
            await self._get_or_create_social_account(
                user_id=user.id,
                social_id=user_info.social_id,
                email=user_info.email,
                provider_slug=self.social_auth_backend.provider_slug,
            )
            return await self.user_service.signin(
                verify_password=False,
                user=auth_depends.UserSignIn(username=user.username, password=""),
                fingerprint=fingerprint,
            )

        raise UserSocialInfoParseError("Cannot parse user info from social provider")

    async def redirect_to_social_provider(
        self, target_auth_url: str, request: Request
    ) -> RedirectResponse:
        logger.debug("SocialAccountService:redirect_to_social_provider")

        if redirect_url := await self.social_auth_backend.authorize_url(
            auth_url=target_auth_url, request=request
        ):
            return RedirectResponse(redirect_url, status_code=302)

        raise SocialServiceError("Cannot redirect_to_social_provider url")

    async def _get_or_create_social_account(
        self, user_id: UUID, social_id: str, email: str, provider_slug: str
    ) -> [social_schemas.SocialAccount, bool]:
        """Get or create social account.

        Args:
            user_id (UUID): User id.
            social_id (UUID): User id in social provider system.
            email (str): User email.
            provider_slug (str): Social provider slug.

        Returns:
            social_schemas.SocialAccount, bool: Social account
                and flag if it was created.
        """
        is_created = False
        if social_account := await self._get_unique_social_account(
            user_id=user_id,
            social_id=social_id,
            email=email,
            provider_slug=provider_slug,
        ):
            logger.debug("Social account already exists: %s", social_account.dict())

            return social_account, is_created

        try:
            social_account = await self.social_account_repo.create(
                user_id=user_id,
                social_id=social_id,
                email=email,
                provider_slug=provider_slug,
            )
            is_created = True

        except sqlalchemy_exc.IntegrityError as err:
            raise SocialAccountAlreadyExistsError from err

        logger.debug("Social account has been created: %s", social_account.dict())

        return social_account, is_created

    async def _get_unique_social_account(
        self,
        user_id: UUID,
        social_id: str,
        email: str,
        provider_slug: str,
    ) -> social_schemas.SocialAccount | None:
        if filtered_social_accounts := await self.social_account_repo.filter_by(
            user_id=user_id,
            social_id=social_id,
            email=email,
            provider_slug=provider_slug,
        ):
            return filtered_social_accounts[0]
        return None


async def get_social_account_service(
    social_auth_backend: Annotated[
        social_auth.ISocialAuthBackend, Depends(social_auth.get_social_auth_backend)
    ],
    user_service: Annotated[UserService, Depends(user_depends.get_user_service)],
    db_session: Annotated[AsyncSession, Depends(get_db)],
) -> ISocialAccountService:
    return SocialAccountService(
        social_auth_backend=social_auth_backend,
        social_account_repo=PostgresSocialAccountRepository(async_session=db_session),
        user_service=user_service,
    )
