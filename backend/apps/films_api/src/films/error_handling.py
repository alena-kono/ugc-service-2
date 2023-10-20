from logging import getLogger

from fastapi import Request
from fastapi.responses import RedirectResponse
from src.common.exceptions import AuthIsUnavailableError

logger = getLogger("root")


async def personalized_content_graceful_degradation(
    request: Request,
    exc: AuthIsUnavailableError,
) -> RedirectResponse:
    """
    This function implements the graceful degradation of the service.
    If the auth service is unavailable, we will return the default response.

    Args:
        request: Request object.
        exc: AuthIsUnavailableError object.

    Returns:
        RedirectResponse object.
    """
    logger.warning(
        f"Auth service is unavailable. Applying a graceful degradation strategy."
        f"Request: {request.url.path}"
    )

    return RedirectResponse(
        url="/api/v1/films", headers={"X-Auth-Service-Unavailable": "true"}
    )
