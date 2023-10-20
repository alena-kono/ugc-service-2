from src.common.cache import AbstractCache


class JWTStorage:
    """JWT storage that contains revoked tokens."""

    def __init__(self, cache: AbstractCache) -> None:
        self.cache = cache

    async def is_token_revoked(self, jti: str) -> bool:
        """Check that jti (JWT id) is revoked."""
        return bool(await self.cache.exist(jti))

    async def revoke_token(self, jti: str, expire_secs: int) -> bool:
        """Save revoked jti (JWT id) to the cache."""
        return await self.cache.set(key=jti, data="", timeout_secs=expire_secs)
