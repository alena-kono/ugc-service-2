from functools import partial

import backoff
from elasticsearch.exceptions import ConnectionError as ElasticConnectionError
from etl.settings.settings import SystemSettings
from psycopg2.errors import OperationalError as PostgreConnectionError
from redis.exceptions import ConnectionError as RedisConnectionError

system_settings = SystemSettings()

backoff_expo = partial(
    backoff.expo,
    base=2,
    factor=system_settings.factor,
    max_value=system_settings.max_value,
)


etl_backoff = partial(
    backoff.on_exception,
    backoff_expo,
    (
        ElasticConnectionError,
        PostgreConnectionError,
        RedisConnectionError,
        ValueError,
    ),
)
