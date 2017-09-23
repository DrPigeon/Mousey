# -*- coding: utf-8 -*-
import discord

from mousey import Cog, commands, Context, Mousey


class Admin(Cog):
    """Commands for bot admins."""

    async def __local_check(self, ctx: Context):
        return await self.mousey.is_admin(ctx.author)

    @commands.command()
    async def reply(self, ctx: Context, user: discord.User, *, message: str):
        """Reply to feedback. This sends the user a direct message."""
        embed = discord.Embed(title='Feedback Reply', description=message, color=ctx.color)
        embed.set_author(name=f'{ctx.author} {ctx.author.id}', icon_url=ctx.author.avatar_url)
        embed.set_footer(text='To respond to this please use the feedback command again!')

        try:
            await user.send(embed=embed)
        except discord.HTTPException as e:
            await ctx.send(f'Sending the reply failed: {type(e).__name__} {e}')
        else:
            await ctx.ok()


def setup(mousey: Mousey):
    mousey.add_cog(Admin(mousey))
