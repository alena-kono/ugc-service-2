from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.common import models
from src.common.database import Base


class UsersPermissions(models.UUIDMixin, models.TimeStampedMixin, Base):
    __tablename__ = "users_permissions"

    permission_id: Mapped[UUID] = mapped_column(
        ForeignKey("permissions.id"), primary_key=True
    )
    permission = relationship("Permission", back_populates="users")

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "users.id", name="users_permissions_user_id_fkey", ondelete="CASCADE"
        ),
        primary_key=True,
    )
    user = relationship("User", back_populates="permissions")

    __table_args__ = (
        UniqueConstraint(
            permission_id, user_id, name="unique_together_permission_id_user_id"
        ),
    )


class Permission(models.UUIDMixin, models.TimeStampedMixin, Base):
    __tablename__ = "permissions"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(String(255), default="")

    users = relationship("UsersPermissions", back_populates="permission")

    def __repr__(self) -> str:
        return f"<Permission {self.name}>"
