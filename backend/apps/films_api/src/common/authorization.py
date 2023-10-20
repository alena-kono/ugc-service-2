import http
import time
from typing import Annotated

from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectorError
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer
from jose import jwt
from src.common.clients import get_http_session
from src.common.exceptions import AuthIsUnavailableError
from src.common.schemas import JwtClaims
from src.settings.app import AppSettings

settings = AppSettings()

HttpSession = Annotated[ClientSession, Depends(get_http_session)]


def decode_token(token: str) -> JwtClaims | None:
    try:
        decoded_token = jwt.decode(
            token,
            settings.auth.jwt_secret_key,
            algorithms=[settings.auth.jwt_encoding_algorithm],
        )
        jwt_claims = JwtClaims(**decoded_token)
        return jwt_claims if jwt_claims.exp >= time.time() else None
    except Exception:
        return None


async def verify_token(token: str, session: ClientSession) -> bool:
    url = f"{settings.auth.url}/api/v1/auth/token-verify"
    payload = {"token_string": token}
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    try:
        async with session.post(
            url,
            json=payload,
            headers=headers,
            timeout=settings.auth.request_timeout_sec,
        ) as response:
            if response.status != http.HTTPStatus.OK:
                return False

            data = await response.json()
    except ClientConnectorError as e:
        raise AuthIsUnavailableError() from e

    return data.get("status") == "valid"


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request, session: HttpSession) -> JwtClaims:  # type: ignore
        credentials = await super().__call__(request)
        if not credentials:
            raise HTTPException(
                status_code=http.HTTPStatus.FORBIDDEN,
                detail="Invalid authorization code.",
            )

        if not credentials.scheme == "Bearer":
            raise HTTPException(
                status_code=http.HTTPStatus.UNAUTHORIZED,
                detail="Only Bearer token might be accepted",
            )

        if not await verify_token(credentials.credentials, session):
            raise HTTPException(
                status_code=http.HTTPStatus.FORBIDDEN,
                detail="Invalid or expired token.",
            )

        decoded_token = decode_token(credentials.credentials)

        if not decoded_token:
            raise HTTPException(
                status_code=http.HTTPStatus.FORBIDDEN,
                detail="Invalid or expired token.",
            )

        return decoded_token
