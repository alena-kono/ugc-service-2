from collections import namedtuple

from src.settings.base import BaseAppSettings

RateLimitParams = namedtuple("RateLimitParams", ["times", "seconds"])


class RateLimiterSettings(BaseAppSettings):
    STANDARD_LIMIT = RateLimitParams(times=5, seconds=1)
