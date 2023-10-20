from datetime import datetime, timedelta
from typing import Any, Container

from jose import jwt as jose_jwt


async def encode_jwt(
    claims: dict[str, Any],
    key: str,
    expires_delta: timedelta,
    token_type: str,
    algorithm: str,
    additional_claims: dict[str, Any] | None = None,
) -> str:
    now = datetime.utcnow()
    data_to_encode = claims.copy()
    data_to_encode.update(
        {
            "type": token_type,
            "exp": now + expires_delta,
            "iat": now,
        }
    )
    if additional_claims:
        data_to_encode.update(additional_claims)
    return jose_jwt.encode(claims=data_to_encode, key=key, algorithm=algorithm)


async def decode_jwt(
    token: str, key: str, algorithms: Container[str]
) -> dict[str, Any]:
    return jose_jwt.decode(token=token, key=key, algorithms=algorithms)
