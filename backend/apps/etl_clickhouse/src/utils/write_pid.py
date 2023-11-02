import logging
import os

logger = logging.getLogger(__name__)


def write_pid(path: str) -> None:
    with open(path, "w", encoding="utf-8") as file:
        pid = os.getpid()
        logger.info(f"Writing etl pid = {pid} to pidfile")

        file.write(str(pid))
        file.flush()
