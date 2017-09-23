# -*- coding: utf-8 -*-
import discord

from mousey import Cog, commands, Context, Mousey
from mousey.const import FEEDBACK_CHANNEL


class Utility(Cog):
    """Beep boop!"""

    @commands.command()
    async def feedback(self, ctx: Context, *, message: str):
        """Send feedback about Mousey."""
        embed = discord.Embed(description=message, color=ctx.color)
        embed.set_author(name=f'{ctx.author} {ctx.author.id}', icon_url=ctx.author.avatar_url)

        embed.add_field(
            name='User',
            value=f'{ctx.author} {ctx.author.id}'
        )
        embed.add_field(
            name='Location',
            value=f'{ctx.guild.name} {ctx.guild.id}' if ctx.guild is not None else 'direct message'
        )

        channel = self.mousey.get_channel(FEEDBACK_CHANNEL)
        await channel.send(embed=embed)
        await ctx.ok()

    @commands.command(aliases=['oauth'])
    async def invite(self, ctx: Context):
        """Mouseys oauth2 authorization link."""
        perms = discord.Permissions()
        perms.add_reactions = True
        perms.attach_files = True
        perms.ban_members = True
        perms.change_nickname = True
        perms.connect = True
        perms.deafen_members = True
        perms.embed_links = True
        perms.external_emojis = True
        perms.kick_members = True
        perms.manage_channels = True
        perms.manage_guild = True
        perms.manage_messages = True
        perms.manage_nicknames = True
        perms.manage_roles = True
        perms.move_members = True
        perms.mute_members = True
        perms.read_message_history = True
        perms.read_messages = True
        perms.send_messages = True
        perms.view_audit_log = True

        await ctx.send(f'<{discord.utils.oauth_url(self.mousey.user.id, perms)}>')


def setup(mousey: Mousey):
    mousey.add_cog(Utility(mousey))
