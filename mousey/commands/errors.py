# -*- coding: utf-8 -*-
from discord.ext.commands.errors import *

from .context import Context


__all__ = (
    'BadArgument',
    'CheckFailure',
    'CommandError',
    'CommandInvokeError',
    'CommandNotFound',
    'CommandOnCooldown',
    'DisabledCommand',
    'InsufficientPermissions',
    'MissingPermissions',
    'MissingRequiredArgument',
    'NoPrivateMessage',
    'NoSubCommand',
    'NotOwner',
    'TooManyArguments',
    'UserInputError',
)


# I know commands.BotMissingPermissions exists, but I don't like the error message
class InsufficientPermissions(CheckFailure):
    """Exception raised when the bot does not have permissions needed to execute a command."""

    def __init__(self, **perms):
        self.missing = ', '.join(x.replace('_', ' ') for x in perms.keys())

    def __str__(self):
        return f'Can\'t execute command! I\'m missing the following permissions: {self.missing}'


class NoSubCommand(CommandError):
    """Exception which can be raised in empty command groups, triggers an informative error message."""

    def __init__(self, ctx: Context):
        self.message = f'No subcommand used! See "{ctx.prefix} {ctx.command}" for a list of available commands!'

    def __str__(self):
        return self.message
