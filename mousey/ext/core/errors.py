# -*- coding: utf-8 -*-
import datetime
import traceback
from typing import List

import discord

from mousey import Cog, commands, Context, Mousey
from mousey.const import DENY_EMOJI, ERROR_CHANNEL
from mousey.ext.internal.testing import TestError


IGNORED_ERRORS = (
    commands.CommandNotFound,
    commands.CheckFailure,
    commands.NoPrivateMessage,
    commands.NotOwner,
    commands.DisabledCommand,
)


def sentence(content: str) -> str:
    """Capitalizes the first letter in a string and appends a full stop if none is found."""
    if not content.endswith('.'):
        content = f'{content}.'
    return content[0].upper() + content[1:]


class Errors(Cog):
    """Monitors errors, gives the user useful error messages and reports them internally."""

    def __init__(self, mousey: Mousey):
        super().__init__(mousey)

        # the on_error event only gets dispatched to normal discord.Client listeners,
        # not additional ones from the commands extension
        self.old_on_error = mousey.on_error
        mousey.on_error = self.on_error

    def __unload(self):
        self.mousey.on_error = self.old_on_error

    async def on_error(self, event: str, *args, **kwargs):
        trace = traceback.format_exc(limit=15)
        await self.send_error_log(f'Event: {event}', trace)

    async def on_command_error(self, ctx: Context, error: commands.CommandError):
        if isinstance(error, IGNORED_ERRORS):
            return

        prefix = ctx.prefix
        command = ctx.command.qualified_name

        if isinstance(error, commands.BadArgument):
            return await ctx.send(f'Bad argument! {error}. See "{prefix}help {command}" for information.')

        if isinstance(error, commands.TooManyArguments):
            return await ctx.send(f'Too many arguments! See "{prefix}help {command}" for information.')

        if isinstance(error, commands.MissingRequiredArgument):
            error = sentence(str(error))
            return await ctx.send(f'Missing argument! {error} See "{prefix}help {command}" for information.')

        if isinstance(error, (commands.InsufficientPermissions, commands.NoSubCommand, TestError)):
            return await ctx.send(str(error))

        # no need to have the extra traceback for the CommandInvokeError raising
        if isinstance(error, commands.CommandInvokeError):
            error = error.original

        try:
            await ctx.send(f'{DENY_EMOJI} Something went wrong! The bot owner has been notified.')
        except discord.HTTPException:
            pass  # no perms etc

        user = ctx.author
        guild = ctx.guild

        trace = traceback.format_exception(type(error), error, error.__traceback__, limit=15)
        actual_trace = '\n'.join(trace)

        fields = [
            {
                'name': 'User',
                'value': f'{user.name} {user.id}'
            },
            {
                'name': 'Location',
                'value': f'{guild.name} {guild.id}' if guild is not None else 'direct message'
            },
        ]

        await self.send_error_log(f'Command: {command}', actual_trace, fields)

    async def on_scheduled_error(self, method: str, error: Exception):
        trace = traceback.format_exception(type(error), error, tb=error.__traceback__, limit=15)
        actual_trace = '\n'.join(trace)
        await self.send_error_log(f'Schedule: {method}', actual_trace)

    async def send_error_log(self, error_title: str, trace: str, fields: List[dict]=None):
        """Send a message to the error reporting channel in discord."""
        channel = self.mousey.get_channel(ERROR_CHANNEL)

        embed = discord.Embed(
            title=error_title,
            description=f'```py\n{trace}```',
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color(0x8f9eee)
        )

        if fields:
            for field in fields:
                embed.add_field(**field)

        await channel.send(embed=embed)


def setup(mousey: Mousey):
    mousey.add_cog(Errors(mousey))
