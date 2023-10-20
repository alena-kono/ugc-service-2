from time import sleep

from etl.logic.elastic_search.elastic_loader import (
    get_es_client,
    load_es_schemas,
    run_es_loaders,
)
from etl.logic.postgresql.client import PostgreClient
from etl.logic.postgresql.runner import run_postgre_layers
from etl.logic.state.state import RedisState
from etl.logic.storage.storage import Storage
from etl.logic.transformer.transformers import run_transformers
from etl.settings.settings import ESSettings, PGSettings, RedisSettings, SystemSettings
from loguru import logger


def main() -> None:
    logger.info("ETL has been started")

    pg_settings = PGSettings()  # type: ignore
    es_settings = ESSettings()  # type: ignore
    redis_settings = RedisSettings()  # type: ignore
    system_settings = SystemSettings()

    state = RedisState(settings=redis_settings)
    pg_client = PostgreClient(pg_settings)
    es_client = get_es_client(es_settings)
    storage = Storage()

    load_es_schemas(es_client)
    while True:
        logger.info("Runnig the synchronization process")
        storage.clean()

        state.publish_state()
        state.update_state()

        for _ in run_postgre_layers(pg_client):
            run_transformers()
            run_es_loaders(es_client)

        state.store_state()

        logger.info("Going to sleep")
        sleep(system_settings.synhronization_time_sec)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("Stop the ETL process")
