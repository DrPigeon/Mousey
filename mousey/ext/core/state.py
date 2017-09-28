# -*- coding: utf-8 -*-
import discord

from mousey import Cog, commands, Context, Mousey


class State(Cog):
    """Cog to keep the database updated."""

    async def on_ready(self):
        pass  # todo: resync db

    async def on_guild_join(self, guild: discord.Guild):
        async with self.db.acquire() as conn:
            query = """
                INSERT INTO guilds (
                    guild_id, created_at, joined_at, owner_id, config
                )
                VALUES (
                    $1, $2, $3, $4, $5
                )
                ON CONFLICT (
                    guild_id
                )
                DO UPDATE SET joined_at = $3, owner_id = $4
            """
            await conn.execute(query, guild.id, guild.created_at, guild.me.joined_at, guild.owner_id, '{}')

    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
        if before.owner == after.owner:
            return

        async with self.db.acquire() as conn:
            query = 'UPDATE guilds SET owner_id = $2 WHERE guild_id = $1'
            await conn.execute(query, before.id, after.owner_id)

    async def on_guild_remove(self, guild: discord.Guild):
        # guilds get kept because the config should be preserved
        async with self.db.acquire() as conn:
            query = 'UPDATE guilds SET joined_at = NULL WHERE guild_id = $1'
            await conn.execute(query, guild.id)

    @commands.command(typing=True)
    @commands.is_owner()
    async def sync(self, ctx: Context):
        """Syncs Mouseys state to the database."""
        async with self.db.acquire() as conn:
            query = """
                INSERT INTO guilds (
                    guild_id, created_at, joined_at, owner_id, config
                )
                VALUES (
                    $1, $2, $3, $4, $5
                )
                ON CONFLICT (
                    guild_id
                )
                DO UPDATE SET joined_at = $3, owner_id = $4
            """

            guilds = ((x.id, x.created_at, x.me.joined_at, x.owner_id, '{}') for x in self.mousey.guilds)
            await conn.executemany(query, guilds)

        await ctx.ok()


def setup(mousey: Mousey):
    mousey.add_cog(State(mousey))
