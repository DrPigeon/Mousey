# -*- coding: utf-8 -*-
import asyncio
import logging

import aioredis
import asyncpg
import uvloop

from config import POSTGRES_CRED, REDIS_CRED, TOKEN
from mousey import Mousey


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='mousey.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


async def run():
    db = await asyncpg.create_pool(**POSTGRES_CRED)
    redis = await aioredis.create_pool(REDIS_CRED)

    mousey = Mousey(db=db, redis=redis)

    await mousey.start(TOKEN)


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
