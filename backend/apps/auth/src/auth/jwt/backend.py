from src.auth.jwt import schemas as jwt_schemas
from src.auth.jwt.service import create_tokens
from src.auth.jwt.storage import JWTStorage
from src.settings.app import get_app_settings
from typing_extensions import Self

settings = get_app_settings()


class JWTAuthorizationBackend:
    """Authorization backend that uses JWT."""

    def __init__(self, jwt_storage: JWTStorage) -> None:
        self.jwt_storage = jwt_storage

    def __call__(self) -> Self:
        return self

    async def generate_jwt_credentials(
        self, user_identity: jwt_schemas.JWTUserIdentity
    ) -> jwt_schemas.JWTCredentials:
        token_identity = jwt_schemas.JWTIdentity.from_user_identity(user=user_identity)
        access_token, refresh_token = await create_tokens(identity=token_identity)
        return jwt_schemas.JWTCredentials(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def refresh_jwt_credentials(
        self,
        decoded_token: jwt_schemas.JWTDecoded,
    ) -> jwt_schemas.JWTCredentials:
        """Renew jwt credentials using a refresh token."""
        await self.revoke_jwt_credentials(decoded_token)
        return await self.generate_jwt_credentials(user_identity=decoded_token.user)

    async def revoke_jwt_credentials(
        self, decoded_token: jwt_schemas.JWTDecoded
    ) -> None:
        """Revoke jwt credentials by their jtis (JWT IDs)."""
        await self.jwt_storage.revoke_token(
            jti=decoded_token.access_jti,
            expire_secs=settings.auth.access_token_expires_secs,
        )
        await self.jwt_storage.revoke_token(
            jti=decoded_token.refresh_jti,
            expire_secs=settings.auth.refresh_token_expires_secs,
        )
        return None

    async def verify_jwt_credentials_are_active(
        self, decoded_token: jwt_schemas.JWTDecoded
    ) -> bool:
        """Verify that all jwt credentials are active (not revoked)."""
        tokens_jtis = (decoded_token.access_jti, decoded_token.refresh_jti)
        are_active = [
            not await self.jwt_storage.is_token_revoked(jti) for jti in tokens_jtis
        ]
        return all(are_active)
