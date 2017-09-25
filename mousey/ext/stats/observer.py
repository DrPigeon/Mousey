# -*- coding: utf-8 -*-
import datetime
import logging

import discord

from config import DBOTS_TOKEN
from mousey import Cog, commands, Mousey
from mousey.const import GUILDS_CHANNEL, USER_AGENT
from mousey.utils import clean_text


DBOTS_BASE = 'https://bots.discord.pw/api'


log = logging.getLogger(__name__)


class Observer(Cog):
    """Cog to observe and report Mouseys usage statistics to various places"""

    async def on_ready(self):
        await self.post_stats()

    async def on_guild_join(self, guild: discord.Guild):
        log.info(f'joined guild {guild.name} {guild.id}')

        try:
            msg = (f'\N{LARGE BLUE CIRCLE} {guild.name} {guild.id} - '
                   f'{len(guild.roles)} role(s) - {guild.member_count} members - {guild.owner}')

            guild_feed = self.mousey.get_channel(GUILDS_CHANNEL)
            await guild_feed.send(clean_text(guild_feed, msg))
        except discord.HTTPException:
            pass

        await self.post_stats()

    async def on_guild_remove(self, guild: discord.Guild):
        log.info(f'left guild {guild.name} {guild.id}')

        try:
            msg = f'\N{LARGE RED CIRCLE} {guild.name} {guild.id}'

            guild_feed = self.mousey.get_channel(GUILDS_CHANNEL)
            await guild_feed.send(clean_text(guild_feed, msg))
        except discord.HTTPException:
            pass

        await self.post_stats()

    async def on_command_completion(self, ctx: commands.Context):
        # log how many commands are used in which guilds
        guild_id = ctx.guild.id if ctx.guild is not None else ctx.channel.id

        async with self.db.acquire() as conn:
            query = 'INSERT INTO commands (guild_id, author_id, command, used_at) VALUES ($1, $2, $3, $4)'
            await conn.execute(
                query, guild_id, ctx.author.id, ctx.command.qualified_name, datetime.datetime.utcnow()
            )

    async def post_stats(self):
        """Post bot statistics to https://bots.discord.pw/."""
        if self.mousey.user.id != 288369203046645761:
            return  # no need to report on test bots, forks

        count = self.mousey.guild_count

        data = {
            'server_count': count
        }
        headers = {
            'Authorization': DBOTS_TOKEN,
            'User-Agent': USER_AGENT
        }
        url = f'{DBOTS_BASE}/bots/{self.mousey.user.id}/stats'

        async with self.session.post(url, headers=headers, json=data) as resp:
            log.info(f'reported to dbots. status: {resp.status}, reason: {resp.reason}')


def setup(mousey: Mousey):
    mousey.add_cog(Observer(mousey))
