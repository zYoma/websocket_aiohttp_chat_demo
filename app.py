import asyncio
import pathlib

from aiohttp import web
from loguru import logger

import routes
from config.settings import databases_
from middlewares import log_middleware


PROJ_ROOT = pathlib.Path(__file__).parent.parent


async def init_app(build='development', databases=databases_) -> web.Application:
    """
    Иницализация сервера

    :param build: Билд определяет, какие бинды будут прокидываться для БД.
    Возможные значения на данный момент: 'development' & 'test'
    :type build: str
    :type databases: dict
    :return: ``aiohttp.web.Application()``
    """
    loop = asyncio.get_event_loop()
    loop.set_debug(True)

    app = web.Application()
    
    app.wslist = {}

    middlewares = [
        log_middleware,
    ]

    # --- Прокидывем роуты
    for route in routes.routes:
        if len(route) > 2:
            app.router.add_route(*route)
        else:
            app.router.add_view(*route)

    db_tasks = []
    # --- Настройка БД
    for x in databases:
        db_tasks.extend([
            x.db.configure_settings(build=build),
            x.db.start_engine(app=app, extracted_engine=x.engine)
        ])
        middlewares.append(x.engine)

    await asyncio.gather(*db_tasks)
    logger.info('Initialized DB')

    app.middlewares.extend(middlewares)

    app.on_startup.append(on_start)
    app.on_shutdown.append(on_shutdown)

    return app

async def on_start(app):
    pass


async def on_shutdown(app: web.Application) -> None:
    for ws in list(app.wslist.values()):
        await ws.close()
