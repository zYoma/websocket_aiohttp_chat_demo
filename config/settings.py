import logging.config
import os
from dataclasses import dataclass
from distutils.util import strtobool
from typing import Type

from dotenv import load_dotenv, find_dotenv
from gino_aiohttp import Gino
from utils.db import GinoDB


# --- Подгружаем переменные окружения, обновляя существующие с предыдущего запуска
load_dotenv(find_dotenv(), override=True, verbose=True)

DB_BINDINGS = {
    "chat": {
        "development": {
            "dsn": os.getenv("CHAT_DB_URL"),
            "user": os.getenv("CHAT_DB_USER"),
            "password": os.getenv("CHAT_DB_PASSWORD"),
            "database": os.getenv("CHAT_DB_NAME"),
            "host": os.getenv("CHAT_DB_HOST"),
        },
         "test": {
            "dsn": os.getenv("TEST_DB_URL"),
            "user": os.getenv("TEST_DB_USER"),
            "password": os.getenv("TEST_DB_PASSWORD"),
            "database": os.getenv("TEST_DB_NAME"),
            "host": os.getenv("TEST_DB_HOST"),
            "port": os.getenv("TEST_DB_PORT"),
        },
    },
}


@dataclass
class ProjectGinoDB(GinoDB):
    """
        Модифицирует __init__, чтобы при инициализации не прокидывать
        аттрибут db_settings дважды в оба объекта
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, db_settings=DB_BINDINGS)


# Создаем базы, которые сами вытащат свои креденшиалы из глобальных настроек
# и выносим их engine для импортирования
CHAT_DB = ProjectGinoDB(name="chat", build="development")
CHAT_ENGINE = CHAT_DB.engine()


@dataclass
class DBConf:
    db: Type[ProjectGinoDB]
    engine: Type[Gino]


databases_ = [
    DBConf(CHAT_DB, CHAT_ENGINE),
]


# /alembic db for tests
ALEMBIC_TEST_DB = os.getenv('ALEMBIC_TEST_DB')

# Включить логирование SQL
SQL_LOGS = bool(strtobool(os.getenv("SQL_LOGS")))


LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "colored": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s[%(levelname)s] %(asctime)s:%(name)s:%(reset)s %(white)s%(message)s",
            "log_colors": {
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red",
            },
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "colored",
            "stream": "ext://sys.stdout",
        }
    },
    "root": {"level": "INFO", "handlers": ["console"]},
    "disable_existing_loggers": False,
}

if SQL_LOGS:
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger('root')

