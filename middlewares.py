# -*- coding: utf-8 -*-
import asyncio

from aiohttp import web
from loguru import logger


async def logger_info(msg, ):
    logger.info(msg)


@web.middleware
async def log_middleware(request, handler):
    response = await handler(request)
    short_msg = f'{request._rel_url.path}: STATUS: {getattr(response, "status", "ERROR")} '

    other_msg = [
        lambda: short_msg,
    ]
    for x in other_msg:
        asyncio.ensure_future(logger_info(x()))

    return response
