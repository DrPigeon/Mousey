# -*- coding: utf-8 -*-
import json

from mousey import Cog, commands, Context, Mousey


class Config(Cog):
    def __init__(self, mousey: Mousey):
        super().__init__(mousey)

        self.configs = {}

    async def get(self, guild_id: int) -> dict:
        """Returns a guilds configuration, either from memory or the database."""
        if guild_id in self.configs:
            return self.configs[guild_id]

        self.configs[guild_id] = config = await self._get(guild_id)
        return config

    async def put(self, guild_id: int, config: dict):
        """Save a guild config. This stores it in the database and in memory."""
        self.configs[guild_id] = config
        await self._put(guild_id, config)

    async def _get(self, guild_id: int):
        async with self.db.acquire() as conn:
            query = 'SELECT config FROM guilds WHERE guild_id = $1'
            result = await conn.fetchval(query, guild_id)
        return json.loads(result)

    async def _put(self, guild_id: int, config: dict):
        config = json.dumps(config)

        async with self.db.acquire() as conn:
            query = 'UPDATE guilds SET config = $1 WHERE guild_id = $2'
            await conn.execute(query, config, guild_id)

    @commands.command()
    @commands.is_owner()
    async def clear_configs(self, ctx: Context):
        """Clears the configs cached in memory."""
        self.configs = {}
        await ctx.ok()


def setup(mousey: Mousey):
    mousey.add_cog(Config(mousey))
