# -*- coding: utf-8 -*-
import discord

from mousey import Cog, commands, Context, Mousey


class State(Cog):
    """Cog to keep the database updated."""

    async def on_ready(self):
        await self.sync()

    async def on_guild_join(self, guild: discord.Guild):
        async with self.db.acquire() as conn:
            query = """
                INSERT INTO guilds (
                    guild_id, created_at, name, icon, joined_at, owner_id
                )
                VALUES (
                    $1, $2, $3, $4, $5, $6
                )
                ON CONFLICT (
                    guild_id
                )
                DO UPDATE SET name = $3, icon = $4, joined_at = $5, owner_id = $6
            """
            await conn.execute(
                query, guild.id, guild.created_at, guild.name, guild.icon, guild.me.joined_at, guild.owner_id,
            )

    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
        if before.name == after.name and before.icon == after.icon and before.owner == after.owner:
            return

        async with self.db.acquire() as conn:
            query = 'UPDATE guilds SET name = $1, icon = $2, owner_id = $3 WHERE guild_id = $4'
            await conn.execute(query, after.name, after.icon, after.owner_id, after.id)

    async def on_guild_remove(self, guild: discord.Guild):
        # guilds get kept to preserve the config
        async with self.db.acquire() as conn:
            query = 'UPDATE guilds SET joined_at = NULL WHERE guild_id = $1'
            await conn.execute(query, guild.id)

    @commands.command(name='sync', typing=True)
    @commands.is_owner()
    async def sync_(self, ctx: Context):
        """Syncs Mouseys state to the database."""
        await self.sync()
        await ctx.ok()

    async def sync(self):
        async with self.db.acquire() as conn:
            query = """
                INSERT INTO guilds (
                    guild_id, created_at, name, icon, joined_at, owner_id
                )
                VALUES (
                    $1, $2, $3, $4, $5, $6
                )
                ON CONFLICT (
                    guild_id
                )
                DO UPDATE SET name = $3, icon = $4, joined_at = $5, owner_id = $6
            """
            guilds = (
                (x.id, x.created_at, x.name, x.icon, x.me.joined_at, x.owner_id) for x in self.mousey.guilds
            )
            await conn.executemany(query, guilds)


def setup(mousey: Mousey):
    mousey.add_cog(State(mousey))
