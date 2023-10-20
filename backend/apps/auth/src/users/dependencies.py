from typing import Annotated
from uuid import UUID

from fastapi import Depends
from pydantic import BaseModel
from src.auth import dependencies as auth_depends
from src.auth.jwt.backend import JWTAuthorizationBackend
from src.users.repositories import (
    UserRepository,
    UserSignInHistoryRepository,
    get_user_repository,
    get_user_sign_in_history_repository,
)
from src.users.service import IUserService, UserService


class User(BaseModel):
    username: str
    first_name: str
    last_name: str


class UserPermission(BaseModel):
    permission_id: UUID


class PasswordChange(BaseModel):
    old_password: str
    password: str


async def get_user_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    log_repository: Annotated[
        UserSignInHistoryRepository, Depends(get_user_sign_in_history_repository)
    ],
    jwt_auth_backend: Annotated[
        JWTAuthorizationBackend, Depends(auth_depends.get_auth_backend)
    ],
) -> IUserService:
    return UserService(
        user_repository=user_repository,
        log_repository=log_repository,
        jwt_auth_backend=jwt_auth_backend,
    )
