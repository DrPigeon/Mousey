# -*- coding: utf-8 -*-
import discord

from mousey import Cog, commands, Context, Mousey


class Blocks(Cog):
    """
    Global Mousey blocks.

    These exclude users from using Mousey commands, they are however still affected by filters and the anti spam system.
    """

    async def __local_check(self, ctx: Context) -> bool:
        return await self.mousey.is_owner(ctx.author)

    async def __global_check(self, ctx: Context) -> bool:
        with await self.redis as conn:
            return not await conn.sismember('mousey:blocks', ctx.author.id)

    @commands.command()
    async def block(self, ctx: Context, user: discord.User, *, reason: str=None):
        """Globally block a user."""
        reason = reason or 'no reason specified'

        async with self.db.acquire() as conn:
            query = """
                INSERT INTO blocks (
                    user_id, reason
                )
                VALUES (
                    $1, $2
                )
                ON CONFLICT (
                    user_id
                )
                DO UPDATE SET reason = $2
            """
            await conn.execute(query, user.id, reason)

        with await self.redis as conn:
            await conn.sadd('mousey:blocks', user.id)

        await ctx.ok()

    @commands.command()
    async def blocked(self, ctx: Context, *, user: discord.User):
        """Shows if someone is blocked and the reason."""
        async with self.db.acquire() as conn:
            query = 'SELECT reason FROM blocks WHERE user_id = $1'
            result = await conn.fetchval(query, user.id)

        if result is None:
            return await ctx.send(f'{user} is not blocked!')

        await ctx.send(f'{user} is blocked for: {result}')

    @commands.command()
    async def unblock(self, ctx: Context, *, user: discord.User):
        """Globally block a user."""
        async with self.db.acquire() as conn:
            query = 'DELETE FROM blocks WHERE user_id = $1'
            await conn.execute(query, user.id)

        with await self.redis as conn:
            await conn.srem('mousey:blocks', user.id)

        await ctx.ok()


def setup(mousey: Mousey):
    mousey.add_cog(Blocks(mousey))
