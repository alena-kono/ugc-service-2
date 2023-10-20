from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.common import models
from src.common.database import Base


class SocialAccount(models.UUIDMixin, models.TimeStampedMixin, Base):
    """Social account db model.

    Constraints:

        - User has only one social account per provider.
        - User has only one email per social account.
        - Social id is unique per provider.
    """

    __tablename__ = "social_accounts"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", name="social_accounts_user_id_fkey", ondelete="CASCADE")
    )
    user = relationship("User", back_populates="social_accounts")

    social_id: Mapped[str] = mapped_column(String(255), nullable=False)
    provider_slug: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            user_id,
            provider_slug,
            name="unique_together_user_id_provider_slug",
        ),
        UniqueConstraint(
            email,
            provider_slug,
            name="unique_together_email_provider_slug",
        ),
        UniqueConstraint(
            social_id,
            provider_slug,
            name="unique_together_social_id_provider_slug",
        ),
    )

    def __repr__(self) -> str:
        return f"<SocialAccount {self.provider_slug} - {self.email}>"
