# -*- coding: utf-8 -*-
import importlib
import pathlib

import discord
from discord.ext import commands

from .context import Context
from .core import GroupMixin
from .formatter import HelpFormatter


# reassignment to have fewer imports in the actual bot code
when_mentioned = commands.when_mentioned
when_mentioned_or = commands.when_mentioned_or


DEFAULT_HELP_ATTRS = {'hidden': True}


class BotBase(GroupMixin, commands.bot.BotBase):
    """
    Extension of the commands.BotBase to provide a few utilities.

    Parameters
    ----------
    approve_emoji : Optional[int]
        ID of a custom emoji which the bot will use when using the Context.ok meth.
        This defaults to a unicode check mark.
    prefixless_dms : bool
        Whether commands in direct messages can be invoked without a prefix. Defaults to False
        This only adds this as an additional prefix, you can still specify prefixes to use.
    """
    def __init__(self, *args, **kwargs):
        formatter = kwargs.pop('formatter', HelpFormatter())
        help_attrs = kwargs.pop('help_attrs', DEFAULT_HELP_ATTRS)

        super().__init__(help_attrs=help_attrs, formatter=formatter, *args, **kwargs)

        self.approve_emoji = kwargs.pop('approve_emoji', None)
        self.prefixless_dms = kwargs.pop('prefixless_dms', False)

    def remove_cog(self, name: str):
        cog = self.cogs.get(name)
        if cog is None:
            return

        # cancel all scheduled tasks made with the @commands.schedule decorator
        tasks = getattr(cog, '_scheduled_tasks', [])
        for task in tasks:
            task.cancel()

        super().remove_cog(name)

    def reload_extension(self, name: str):
        """Reload an extension."""
        self.unload_extension(name)
        self.load_extension(name)

    def recursively_load_extensions(self, path):
        """
        Recursively load all extensions from a directory and its subdirectories.

        .. note:: No errors get handled while loading the extensions, setup may fail at any moment due to bad extensions

        Parameters
        ----------
        path : str
            The path to the directory containing the extensions, separated by /
        """
        path = pathlib.Path(path)

        files = path.glob('**/*.py')
        for file in files:
            if file.stem == '__init__':
                continue

            # remove .py extension and replace / with . for proper import format
            name = str(file).replace('/', '.')[:-3]
            ext = importlib.import_module(name)

            if not hasattr(ext, 'setup'):
                continue  # don't unload again in case this is a required file for an already loaded extension

            self.load_extension(name)

    async def get_prefix(self, message: discord.Message):
        result = await super().get_prefix(message)

        if not isinstance(result, list):
            if self.prefixless_dms and message.guild is None:
                return [result, '']
            return result

        if self.prefixless_dms and message.guild is None:
            result.append('')

        # sort backwards because the parser takes the first match
        return sorted(result, reverse=True)

    async def process_commands(self, message: discord.Message):
        ctx = await self.get_context(message, cls=Context)
        if not ctx.valid:
            return

        await self.invoke(ctx)


class Bot(BotBase, discord.Client):
    pass


class AutoShardedBot(BotBase, discord.AutoShardedClient):
    pass
