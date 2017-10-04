# -*- coding: utf-8 -*-
import discord

from mousey import Cog, commands, Context, Mousey
from mousey.const import DENY_EMOJI, FEEDBACK_CHANNEL


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

    @commands.group(aliases=['prefixes'])
    @commands.guild_only()
    async def prefix(self, ctx: Context):
        """Manage and view prefixes."""
        config = await self.mousey.config.get(ctx.guild.id)

        if 'prefixes' not in config:
            config['prefixes'] = []

        prefixes = config['prefixes'] + [f'<@{self.mousey.user.id}> ']

        # put prefixes in quotes as they may have trailing spaces
        pretty_prefixes = '\n'.join(f'"{x}"' for x in prefixes)

        await ctx.send(f'Current usable prefixes:\n{pretty_prefixes}')

    @prefix.command(name='add')
    @commands.guild_only()
    @commands.has_permissions(check_bot=False, manage_guild=True)
    async def prefix_add(self, ctx: Context, prefix: str):
        """Add a new prefix. To have trailing spaces put it in quotes."""
        config = await self.mousey.config.get(ctx.guild.id)

        if 'prefixes' not in config:
            config['prefixes'] = []

        if len(prefix) > 20:
            return await ctx.send(f'{DENY_EMOJI} prefixes may only be 20 characters long!')

        if len(config['prefixes']) > 10:
            return await ctx.send(f'{DENY_EMOJI} you can only add 10 custom prefixes!')

        # just give the illusion we added it again, even if it exists
        if prefix not in config['prefixes']:
            config['prefixes'].append(prefix)
            await self.mousey.config.save(ctx.guild.id)

        await ctx.send(f'Added "{prefix}" as a prefix', delete_after=10)
        await ctx.ok()

    @prefix.command(name='remove')
    @commands.guild_only()
    @commands.has_permissions(check_bot=False, manage_guild=True)
    async def prefix_remove(self, ctx: Context, prefix: str):
        """Remove a prefix. To remove a prefix with trailing spaces put it in quotes."""
        config = await self.mousey.config.get(ctx.guild.id)

        if 'prefixes' not in config:
            config['prefixes'] = []

        if prefix not in config['prefixes']:
            return await ctx.send(f'{DENY_EMOJI} "{prefix}" is not a valid prefix!')

        config['prefixes'].remove(prefix)
        await self.mousey.config.save(ctx.guild.id)

        await ctx.send(f'Removed "{prefix}" from prefixes.', delete_after=10)
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
