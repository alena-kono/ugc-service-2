from uuid import UUID

from src.common.schemas import AppBaseSchema


class UserSocial(AppBaseSchema):
    """User info from social provider."""

    social_id: str
    provider_slug: str
    email: str


class SocialAccount(AppBaseSchema):
    """User social account schema."""

    user_id: UUID
    social_id: str
    provider_slug: str
    email: str
