from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import INET, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.common import models
from src.common.database import Base
from src.social.models import SocialAccount  # noqa: F401


class User(models.UUIDMixin, models.TimeStampedMixin, Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))

    permissions = relationship(
        "UsersPermissions", back_populates="user", cascade="all, delete"
    )

    user_history = relationship(
        "UserSigninHistory", back_populates="user", cascade="all, delete"
    )

    social_accounts = relationship(
        "SocialAccount", back_populates="user", cascade="all, delete"
    )

    def __repr__(self) -> str:
        return f"<User {self.username}>"


class UserSigninHistory(models.UUIDMixin, models.TimeStampedMixin, Base):
    __tablename__ = "user_login_history"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "users.id", name="user_login_history_user_id_fkey", ondelete="CASCADE"
        )
    )
    user_agent: Mapped[str] = mapped_column(String(255))
    ip_address: Mapped[INET] = mapped_column(INET())

    user: Mapped[User] = relationship(back_populates="user_history")
