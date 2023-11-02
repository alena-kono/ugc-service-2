import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import Field
from src.common import schemas as common_schemas
from src.users import schemas as users_schemas
from typing_extensions import Self


class Status(StrEnum):
    VALID: str = "valid"
    INVALID: str = "invalid"


class StatusDetail(StrEnum):
    VALID: str = "Provided access token is valid"
    INVALID: str = "Provided access token is invalid"


class AccessToken(common_schemas.AppBaseSchema):
    access_token: str = Field(regex=r"^(?:[\w-]*\.){2}[\w-]*$")


class AccessTokenInfo(common_schemas.AppBaseSchema):
    status: Status
    detail: StatusDetail
    provided_access_token: str


class RefreshToken(common_schemas.AppBaseSchema):
    refresh_token: str = Field(regex=r"^(?:[\w-]*\.){2}[\w-]*$")


class JWTCredentials(RefreshToken, AccessToken):
    ...


class JWTUserIdentity(common_schemas.AppBaseSchema):
    id: str
    permissions: list[str]

    @classmethod
    def from_user(cls, user: users_schemas.User) -> Self:
        return cls(
            id=str(user.id),
            permissions=[str(permission_id) for permission_id in user.permissions],
        )


class JWTIdentity(common_schemas.AppBaseSchema):
    user: JWTUserIdentity
    access_jti: str
    refresh_jti: str

    @classmethod
    def from_user_identity(cls, user: JWTUserIdentity) -> Self:
        return cls(
            user=user,
            access_jti=str(uuid.uuid4()),
            refresh_jti=str(uuid.uuid4()),
        )


class JWTDecoded(common_schemas.AppBaseSchema):
    user: JWTUserIdentity
    access_jti: str
    refresh_jti: str
    type: str
    exp: datetime
    iat: datetime
