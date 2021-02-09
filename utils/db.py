import asyncio
from abc import abstractmethod, ABCMeta
from dataclasses import dataclass
from typing import Optional, ClassVar

import asyncpg
from gino_aiohttp import Gino

GlobalDBSettings = dict[str, dict[str, dict[str, Optional[str]]]]


@dataclass
class BaseDB(metaclass=ABCMeta):
    """
    Базовый абстрактный класс для работы с БД

    :param name: наименование базы из ``settings.py``
    :param db_settings: глобальный конфиг. Прим: DB_BINDINGS
    :param build: билд, под который база будет сконфигурирована
    :param cfg: конфиг для конкретного билда
    :cvar engine: `Gino` / `SQLAlchemy`
    """
    name: str
    build: str
    db_settings: GlobalDBSettings
    cfg: dict = None
    engine: ClassVar = None

    @abstractmethod
    async def test_connection(self):
        """
        Корутина для проверки подключения к базе на основе настроек,
        определенных внутри `configure_settings`.
        """
        # Note: as of November 2020 SQLAlchemy does NOT support asyncpg

    @abstractmethod
    async def configure_settings(self, build: str) -> None:
        """
        Корутина для автоматического подборка комплекса настроек для БД
        в зависимости от билда, указанного в ``init_app``. Полученные настройки
        используются в start_engine у объектов с реализацией, где движок явно
        указан внутри класса (см. GinoDB)

        .. code-block:: python

            #app.py
            from settings import mchs_db, mrmr_db


            async def init_app(
                    build='development',
                    enable_auth=ENABLE_AUTH,
                    databases=(mrmr_db, mchs_db))

                #some code

                for db in databases:
                    await db.configure_settings(build=build)
                    middlewares.append(db.engine)
                    # engine logic

        :param build: аргумент `init_app`
        :param app: определяется в теле `init_app`
        :type app: ``aiohttp.web.Application``
        """

    @abstractmethod
    async def start_engine(self, app, extracted_engine) -> None:
        """
        Корутина для работы с engine в классах с реализацией

        # Важно:
        Движок необходимо выносить из класса в модуль settings (см. GinoDB)

        :param app:
        :type app: ``aiohttp.web.Application``
        :param extracted_engine:
        :return:
        """


@dataclass
class GinoDB(BaseDB):
    """
    Значением переменной класса engine становится класс Gino.
    Объекты движка создаются внутри ``settings.py`` отдельно.

    :cvar engine: `Gino`
    """

    engine: ClassVar[Gino] = Gino

    def __post_init__(self):
        self.cfg = self.db_settings[self.name][self.build]

    async def test_connection(self):
        """"""
        conn = await asyncpg.connect(dsn=self.cfg['dsn'])
        asyncio.create_task(conn.close())

    async def configure_settings(self, build):
        """
        Если дефолтный билд, указанный при создании объекта внутри
        ``settings.py`` не соответствует аргументу ``init_app``,
        то самостоятельно переопределяет свой cfg.

        :param build:
        :return:
        """
        if build != self.build and build in self.db_settings[self.name]:
            self.build = build
            self.__post_init__()

        await self.test_connection()

    async def start_engine(self, app, extracted_engine: ClassVar[Gino]):
        """
        Пример использования на проекте mrmr112


        .. code-block:: python

            #settings.py

            @dataclass
            class ProjectGinoDB(GinoDB):

                # Модифицирует __init__, чтобы при инициализации не прокидывать
                # атрибут db_settings дважды в оба объекта

                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs, db_settings=DB_BINDINGS)

            MCHS_DB = ProjectGinoDB(name="mchs112", build="development")
            MCHS_ENGINE = ProjectGinoDB.engine() # движок отдельно

            MRMR_DB = ProjectGinoDB(name="mrmr112", build="development")
            MRMR_ENGINE = ProjectGinoDB.engine() # движок отдельно

            DATABASE_CORES = ((MCHS_DB, MCHS_ENGINE), (MRMR_DB, MRMR_ENGINE))

            # app.py

            async def init_app(build='test',
                               enable_auth=ENABLE_AUTH,
                               databases=DATABASE_CORES) -> web.Application:

            for db, engine in databases:
                await db.configure_settings(build=build)
                await db.start_engine(app=app, extracted_engine=engine)
                logger.debug(engine)

        :param app:
        :type app: ``aiohttp.web.Application``
        :param extracted_engine:
        :type extracted_engine: Gino
        :return:
        """
        dsn = self.cfg['dsn']
        await extracted_engine.set_bind(dsn)
        extracted_engine.init_app(app, self.cfg)
