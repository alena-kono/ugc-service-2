from dotenv import load_dotenv
from loguru import logger
from sqlite_to_postgres.logic.data_types import PGSettings
from sqlite_to_postgres.logic.postgres_saver import PostgresSaver
from sqlite_to_postgres.logic.sqlite_extractor import SQLiteExtractor
from sqlite_to_postgres.settings import settings as env_settings

load_dotenv(env_settings.BASE_DIR.joinpath(".env"))


def load_from_sqlite(settings: env_settings.Settings):
    """Основной метод загрузки данных из SQLite в Postgres"""
    postgre_settings = PGSettings(
        **settings.dict(exclude={"sqlite_file_path", "chunk_size"})
    )

    with SQLiteExtractor(
        settings.sqlite_file_path, settings.chunk_size
    ) as sqlite_extractor, PostgresSaver(
        postgre_settings, settings.chunk_size
    ) as postgres_saver:
        for data in sqlite_extractor.extract_movies():
            postgres_saver.save_all_data(data)


def main() -> None:
    # the settings will be loaded from the env
    settings = env_settings.Settings()  # type: ignore

    logger.info("start transfering")
    load_from_sqlite(settings)


if __name__ == "__main__":
    main()
