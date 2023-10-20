from typing import Iterator

from etl.logic.backoff.backoff import etl_backoff

from .client import PostgreClient
from .enrichers import run_enrichers
from .mergers import run_mergers
from .producers import run_producers


@etl_backoff()
def run_functions(pg_client: PostgreClient) -> None:
    with pg_client as client:
        run_producers(client.connection)
        run_enrichers(client.connection)


def run_generators(pg_client: PostgreClient) -> Iterator[None]:
    with pg_client as client:
        yield from run_mergers(client.connection)


def run_postgre_layers(pg_client: PostgreClient) -> Iterator[None]:
    run_functions(pg_client)
    yield from run_generators(pg_client)
