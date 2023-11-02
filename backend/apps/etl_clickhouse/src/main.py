import asyncio
import logging
import logging.config
import sys

from src.etl.run import run_etl
from src.settings.app import get_app_settings
from src.utils.write_pid import write_pid

settings = get_app_settings()
logging.config.dictConfig(settings.logging.config)

logger = logging.getLogger(__name__)


def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_uncaught_exception


if __name__ == "__main__":
    if settings.pidfile:
        write_pid(settings.pidfile)
    asyncio.run(run_etl(settings))
