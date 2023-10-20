import logging
import secrets
from abc import ABC, abstractmethod
from uuid import UUID

import sqlalchemy
from fastapi_pagination import Page
from src.auth import dependencies as auth_depends
from src.auth.exceptions import UserInvalidCredentialsError, UserUsernameExistsError
from src.auth.jwt import schemas as jwt_schemas
from src.auth.jwt.backend import JWTAuthorizationBackend
from src.users import schemas as users_schemas
from src.users.exceptions import (
    UserDoesNotExistError,
    UserPermissionError,
    UserUpdateError,
)
from src.users.repositories import UserRepository, UserSignInHistoryRepository

logger = logging.getLogger(__name__)


class IUserService(ABC):
    @abstractmethod
    async def signup(self, user: auth_depends.UserSignUp) -> users_schemas.User:
        ...

    @abstractmethod
    async def signin(
        self, user: auth_depends.UserSignIn, fingerprint: auth_depends.UserFingerprint
    ) -> jwt_schemas.JWTCredentials:
        ...

    @abstractmethod
    async def signout(self, decoded_jwt: jwt_schemas.JWTDecoded) -> None:
        ...

    @abstractmethod
    async def get_user_by_id(self, user_id: UUID) -> users_schemas.User:
        ...

    @abstractmethod
    async def get_user_history(
        self, user_id: UUID
    ) -> Page[users_schemas.UserLoginRecord]:
        ...

    @abstractmethod
    async def create_user(
        self, username: str, first_name: str, last_name: str, password: str
    ) -> users_schemas.User:
        ...

    @abstractmethod
    async def change_user_password(
        self, user_id: UUID, old_password: str, new_password: str
    ) -> users_schemas.User:
        ...

    @abstractmethod
    async def assign_user_permission(
        self, user_id: UUID, permission_id: UUID
    ) -> users_schemas.User:
        ...

    @abstractmethod
    async def assign_user_permissions(
        self, user_id: UUID, permission_ids: list[UUID]
    ) -> users_schemas.User:
        ...

    @abstractmethod
    async def revoke_user_permission(
        self, user_id: UUID, permission_id: UUID
    ) -> users_schemas.User:
        ...

    @abstractmethod
    async def update_user_common_info(
        self, user_id: UUID, username: str, first_name: str, last_name: str
    ) -> users_schemas.User:
        ...

    @abstractmethod
    async def get_by_username(self, username: str) -> users_schemas.User | None:
        ...

    @abstractmethod
    async def generate_random_password(self, length: int) -> str:
        ...

    @abstractmethod
    async def delete_user(self, user_id: UUID) -> None:
        ...


class UserService(IUserService):
    def __init__(
        self,
        user_repository: UserRepository,
        log_repository: UserSignInHistoryRepository,
        jwt_auth_backend: JWTAuthorizationBackend,
    ) -> None:
        self.user_repository = user_repository
        self.log_repository = log_repository
        self.jwt_auth_backend = jwt_auth_backend

    async def signup(self, user: auth_depends.UserSignUp) -> users_schemas.User:
        """Register a new user."""
        return await self.create_user(
            username=user.username,
            password=user.password,
            first_name=user.first_name,
            last_name=user.last_name,
        )

    async def signin(
        self,
        user: auth_depends.UserSignIn,
        fingerprint: auth_depends.UserFingerprint,
        verify_password: bool = True,
    ) -> jwt_schemas.JWTCredentials:
        """Authenticate user and save user's signin record."""
        if user_db := await self.get_by_username(user.username):
            is_password_ok = True
            if verify_password:
                is_password_ok = await self.user_repository.check_password(
                    user_id=user_db.id, password=user.password
                )
            if is_password_ok:
                jwt_credentials = await self.jwt_auth_backend.generate_jwt_credentials(
                    jwt_schemas.JWTUserIdentity.from_user(user_db)
                )
                logger.debug("User '%s' has signed in", user_db.username)

                sign_in_record = await self.log_repository.create_record(
                    user_id=user_db.id,
                    user_agent=fingerprint.user_agent,
                    ip_address=str(fingerprint.ip_address),
                )
                logger.debug(
                    "User signin has been saved: %s", str(sign_in_record.dict())
                )

                return jwt_credentials
        raise UserInvalidCredentialsError

    async def signout(self, decoded_jwt: jwt_schemas.JWTDecoded) -> None:
        """Sign out user by revoking user's jwt credentials."""
        await self.jwt_auth_backend.revoke_jwt_credentials(decoded_token=decoded_jwt)

    async def get_user_by_id(self, user_id: UUID) -> users_schemas.User:
        if user := await self.user_repository.get(user_id):
            return user
        raise UserDoesNotExistError(resource_id=user_id)

    async def get_user_history(
        self, user_id: UUID
    ) -> Page[users_schemas.UserLoginRecord]:
        if not await self.user_repository.get(user_id):
            raise UserDoesNotExistError(resource_id=user_id)
        return await self.log_repository.get_user_signin_history(user_id)

    async def create_user(
        self, username: str, first_name: str, last_name: str, password: str
    ) -> users_schemas.User:
        if await self.get_by_username(username=username):
            raise UserUsernameExistsError
        return await self.user_repository.create(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

    async def change_user_password(
        self, user_id: UUID, old_password: str, new_password: str
    ) -> users_schemas.User:
        if not await self.user_repository.get(user_id):
            raise UserDoesNotExistError(resource_id=user_id)

        if not await self.user_repository.check_password(
            user_id=user_id, password=old_password
        ):
            raise UserInvalidCredentialsError

        return await self.user_repository.change_password(user_id, new_password)

    async def assign_user_permission(
        self, user_id: UUID, permission_id: UUID
    ) -> users_schemas.User:
        if not await self.user_repository.get(user_id):
            raise UserDoesNotExistError(resource_id=user_id)

        try:
            return await self.user_repository.assign_permission(user_id, permission_id)
        except sqlalchemy.exc.IntegrityError:
            raise UserPermissionError

    async def assign_user_permissions(
        self, user_id: UUID, permission_ids: list[UUID]
    ) -> users_schemas.User:
        if not await self.user_repository.get(user_id):
            raise UserDoesNotExistError(resource_id=user_id)

        try:
            return await self.user_repository.assign_bulk_permissions(
                user_id, permission_ids
            )
        except sqlalchemy.exc.IntegrityError:
            raise UserPermissionError

    async def revoke_user_permission(
        self, user_id: UUID, permission_id: UUID
    ) -> users_schemas.User:
        if not await self.user_repository.get(user_id):
            raise UserDoesNotExistError(resource_id=user_id)

        try:
            return await self.user_repository.revoke_permission(user_id, permission_id)
        except sqlalchemy.exc.IntegrityError:
            raise UserPermissionError

    async def update_user_common_info(
        self, user_id: UUID, username: str, first_name: str, last_name: str
    ) -> users_schemas.User:
        if not await self.user_repository.get(user_id):
            raise UserDoesNotExistError(resource_id=user_id)

        try:
            return await self.user_repository.update(
                user_id, username, first_name, last_name
            )
        except sqlalchemy.exc.IntegrityError:
            raise UserUpdateError

    async def get_by_username(self, username: str) -> users_schemas.User | None:
        filtered_users = await self.user_repository.filter_by(username=username)
        if filtered_users:
            return filtered_users[0]
        return None

    async def generate_random_password(self, length: int = 16) -> str:
        return secrets.token_hex(nbytes=length)

    async def delete_user(self, user_id: UUID) -> None:
        await self.user_repository.delete_user(user_id)
