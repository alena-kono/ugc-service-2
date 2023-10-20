import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from src.auth import dependencies as auth_depends
from src.auth.jwt import schemas as jwt_schemas
from src.common.utils import build_uri
from src.settings.app import get_app_settings
from src.social.exceptions import InvalidSocialProviderAccessTokenError
from src.social.providers import SocialProviderSlug
from src.social.services import SocialAccountService, get_social_account_service

logger = logging.getLogger(__name__)
settings = get_app_settings()

router = APIRouter()


@router.get(
    path="/signin/{provider_slug:str}",
    response_model=jwt_schemas.JWTCredentials,
    summary="Social sign in",
    description="Sign in with social account",
    response_description="Redirect to social authorization provider",
)
async def social_signin(
    provider_slug: SocialProviderSlug,
    social_account_service: Annotated[
        SocialAccountService, Depends(get_social_account_service)
    ],
    request: Request,
) -> RedirectResponse:
    auth_url = await build_uri(
        request=request, view_name="social_auth", provider_slug=provider_slug.value
    )
    return await social_account_service.redirect_to_social_provider(
        target_auth_url=auth_url, request=request
    )


@router.get(
    path="/auth/{provider_slug:str}",
    response_model=None,
    summary="Social authorization",
    description="Authorize social account",
    response_description=(
        "Access and refresh tokens or redirect to social sign in endpoint"
    ),
)
async def social_auth(
    provider_slug: SocialProviderSlug,
    social_account_service: Annotated[
        SocialAccountService, Depends(get_social_account_service)
    ],
    request: Request,
    user_fingerprint: Annotated[
        auth_depends.UserFingerprint, Depends(auth_depends.get_user_fingerprint)
    ],
) -> jwt_schemas.JWTCredentials | RedirectResponse:
    try:
        return await social_account_service.sign_in_with_social_provider_account(
            request=request, fingerprint=user_fingerprint
        )

    except InvalidSocialProviderAccessTokenError:
        url = await build_uri(
            request=request,
            view_name="social_signin",
            provider_slug=provider_slug.value,
        )
        return RedirectResponse(url=url, status_code=302)
