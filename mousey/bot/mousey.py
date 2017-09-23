# -*- coding: utf-8 -*-
import logging
import time
from typing import Union

import aiohttp
import aioredis
import asyncpg
import discord
import psutil

from .context import Context
from .formatter import HelpFormatter
from mousey import commands
from mousey.const import APPROVE_EMOJI_ID, BOT_OWNERS, EXT_PATH


log = logging.getLogger(__name__)


class Mousey(commands.AutoShardedBot):
    """
    The Mousey Bot.

    Parameters
    ----------
    db : asyncpg.pool.Pool
        The PostgreSQL connection Mousey will use.
    redis : aioredis.RedisPool
        The redis pool Mousey will use for caching.

    Attributes
    ----------
    guild_count : int
        The amount of guilds the bot is connected to. This only includes guilds on the current shard(s), not all guilds.
    process : psutil.Process
        A process instance representing the current process
    session : aiohttp.ClientSession
        A session to use for web requests
    """
    def __init__(self, *args, **kwargs):
        description = "Discord Bot written by FrostLuma#0005 to provide powerful moderation and utility features."
        super().__init__(
            approve_emoji=APPROVE_EMOJI_ID,
            prefixless_dms=True,
            command_prefix=get_prefix,
            formatter=HelpFormatter(),
            description=description,
            *args, **kwargs
        )

        self.db: asyncpg.pool.Pool = kwargs.pop('db')
        self.redis: aioredis.RedisPool = kwargs.pop('redis')

        self.process: psutil.Process = psutil.Process()
        self.session: aiohttp.ClientSession = aiohttp.ClientSession(loop=self.loop)

        self._uptime: float = None
        self.guild_count: int = None

        self.recursively_load_extensions(EXT_PATH)
        log.info(f'loaded {len(self.extensions)} extensions: {", ".join(self.extensions)}')

    async def on_ready(self):
        if self._uptime is None:
            self._uptime = time.monotonic()
        self.guild_count = len(self.guilds)

        log.info('ready')

    async def on_shard_ready(self, shard_id: int):
        log.info(f'shard {shard_id}/{self.shard_count} ready')

    async def on_resumed(self):
        log.info('resumed')

    async def on_guild_join(self, guild: discord.Guild):
        self.guild_count += 1

    async def on_guild_remove(self, guild: discord.Guild):
        self.guild_count -= 1

    @property
    def uptime(self):
        """Property representing the number of seconds passed since Mousey received the READY event"""
        if self._uptime is None:
            return 0
        return time.monotonic() - self._uptime

    async def is_owner(self, user: Union[discord.Member, discord.User]):
        return user.id in BOT_OWNERS  # to allow me using my alt

    async def is_admin(self, user: Union[discord.Member, discord.User]):
        return user.id in BOT_OWNERS  # todo: allow adding more admins via commands, store them

    async def process_commands(self, message: discord.Message):
        ctx = await self.get_context(message, cls=Context)
        if not ctx.valid:
            return

        await self.invoke(ctx)

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        await self.process_commands(message)


async def get_prefix(mousey: Mousey, message: discord.Message):
    mentions = [f'<@{mousey.user.id}> ', f'<@!{mousey.user.id}> ']

    if message.guild is None:
        return mentions

    guild_prefixes = ['~?']  # todo: get from config
    return mentions + guild_prefixes
