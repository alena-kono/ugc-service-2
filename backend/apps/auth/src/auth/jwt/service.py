from datetime import timedelta
from typing import Any

import jose.exceptions as jose_exc
from src.auth.jwt import schemas as jwt_schemas
from src.auth.jwt.exceptions import InvalidJWTError
from src.auth.jwt.utils import decode_jwt, encode_jwt
from src.settings.app import get_app_settings

settings = get_app_settings()


async def validate_jwt(token: str) -> jwt_schemas.JWTDecoded:
    """Validate a JWT string's signature and validate reserved claims."""
    try:
        decoded_token_data = await decode_jwt(
            token=token,
            key=settings.auth.jwt_secret_key,
            algorithms=(settings.auth.jwt_encoding_algorithm,),
        )
    except (jose_exc.JWEError, jose_exc.JWTError) as err:
        raise InvalidJWTError from err

    return jwt_schemas.JWTDecoded(**decoded_token_data)


async def create_tokens(identity: jwt_schemas.JWTIdentity) -> list[str]:
    """Create access and refresh tokens pair with the same identity."""
    tokens = (
        ("access", settings.auth.access_token_expires_secs),
        ("refresh", settings.auth.refresh_token_expires_secs),
    )
    created_tokens = []
    for token_type, token_expire_secs in tokens:
        created_tokens.append(
            await create_token(
                data_to_encode=identity,
                token_type=token_type,
                secret_key=settings.auth.jwt_secret_key,
                expires_delta=timedelta(token_expire_secs),
                algorithm=settings.auth.jwt_encoding_algorithm,
            )
        )
    return created_tokens


async def create_token(
    data_to_encode: jwt_schemas.JWTIdentity,
    token_type: str,
    secret_key: str,
    expires_delta: timedelta,
    algorithm: str,
    additional_claims: dict[str, Any] | None = None,
) -> str:
    return await encode_jwt(
        claims=data_to_encode.dict(),
        key=secret_key,
        expires_delta=expires_delta,
        token_type=token_type,
        algorithm=algorithm,
        additional_claims=additional_claims,
    )
