from abc import ABC, abstractmethod
from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.database import get_db
from src.social import models as social_models
from src.social import schemas as social_schemas


class SocialAccountRepository(ABC):
    @abstractmethod
    async def create(
        self, user_id: UUID, social_id: str, provider_slug: str, email: str
    ) -> social_schemas.SocialAccount | None:
        ...

    @abstractmethod
    async def filter_by(self, **kwargs: Any) -> list[social_schemas.SocialAccount]:
        ...


class PostgresSocialAccountRepository(SocialAccountRepository):
    def __init__(self, async_session: AsyncSession) -> None:
        self.async_session = async_session

    async def create(
        self, user_id: UUID, social_id: UUID, provider_slug: str, email: str
    ) -> social_schemas.SocialAccount:
        social_account = social_models.SocialAccount(
            user_id=user_id,
            social_id=social_id,
            provider_slug=provider_slug,
            email=email,
        )
        self.async_session.add(social_account)
        await self.async_session.commit()

        return social_schemas.SocialAccount.from_orm(social_account)

    async def filter_by(self, **kwargs: Any) -> list[social_schemas.SocialAccount]:
        stmt = select(social_models.SocialAccount).filter_by(**kwargs)

        result = await self.async_session.execute(stmt)

        social_accounts = result.unique().scalars().all()
        return [
            social_schemas.SocialAccount(
                user_id=account.user_id,
                social_id=account.social_id,
                provider_slug=account.provider_slug,
                email=account.email,
            )
            for account in social_accounts
        ]


async def get_social_account_repository(
    db_session: Annotated[AsyncSession, Depends(get_db)]
) -> SocialAccountRepository:
    return PostgresSocialAccountRepository(db_session)
