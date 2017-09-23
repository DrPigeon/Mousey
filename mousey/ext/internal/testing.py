# -*- coding: utf-8 -*-
import asyncio

from mousey import Cog, commands, Context, Mousey
from mousey.const import CHEESE_VOICE_CHANNEL, MOUSEY_GUILD, DENY_EMOJI


class TestError(commands.CommandError):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message


class UnhandledTestError(commands.CommandError):
    pass


class TwoWords(commands.Converter, commands.ViewConverter):
    """Converter which shows off the usage of ViewConverters and RecalledArguments."""
    async def convert(self, ctx: Context, view: commands.StringView):
        # the view can be used to iterate over words using the words meth. ViewConveter has
        words = []
        for word in self.words(view):
            words.append(word)
            # could break out of the loop if a word can not be used

        # the first two words are what the converter actually returns
        ret = ' '.join(words[:2])
        # the rest can be returned using RecalledArgument, will be used on the next parameter of the command
        rest = ' '.join(words[2:])
        return ret, commands.RecalledArgument(rest)


class Optional(commands.Converter):
    """Converter which just returns the whole argument if it's not a number, to test default consume all parameters."""
    async def convert(self, ctx: Context, argument: str):
        words = argument.split()
        if words[0].isdigit():
            rest = ' '.join(words[1:])
            return words[0], commands.RecalledArgument(rest)
        return commands.RecalledArgument(argument)


class Testing(Cog):
    """Cog to test out various things."""

    async def __local_check(self, ctx: Context):
        return await self.mousey.is_admin(ctx.author)

    async def on_ready(self):
        await self.maybe_connect()

    async def on_resumed(self):
        await self.maybe_connect()

    async def maybe_connect(self):
        """Connects to a specified voice channel to indicate Mousey is online."""
        guild = self.mousey.get_guild(MOUSEY_GUILD)
        if guild is None:
            return  # different shard

        state = guild.voice_client
        if state is not None:
            return

        cheese = self.mousey.get_channel(CHEESE_VOICE_CHANNEL)
        await cheese.connect()

    @commands.command()
    async def error(self, ctx: Context, unhandled: bool=False):
        """Raises a test error."""
        if unhandled:
            raise UnhandledTestError('This is an unhandled test error.')

        raise TestError(f'{DENY_EMOJI} Hullo World! This is an error message.')

    @commands.command(typing=True)
    async def type_test(self, ctx: Context, duration: int=10):
        """Tests typing commands."""
        await asyncio.sleep(duration)
        await ctx.ok()

    @commands.group()
    async def convert(self, ctx: Context):
        """Testing of converters."""
        raise commands.NoSubCommand()

    @convert.command()
    async def multi(self, ctx: Context, *, words: TwoWords, rest: str):
        """Multi word consume rest argument, then consume rest."""
        await ctx.send(f'first two words: {words}, rest: {rest}')

    @convert.command()
    async def defaults(self, ctx: Context, *, words: TwoWords='a b', rest: str='c'):
        """Multi word consume rest argument, then consume rest. Both have defaults.."""
        await ctx.send(f'first two words: {words}, rest: {rest}')

    @convert.command()
    async def optional(self, ctx: Context, *, optional: Optional='this is default', rest: str):
        """Optional number argument, then consume rest."""
        await ctx.send(f'optional: {optional}, rest: {rest}')


def setup(mousey: Mousey):
    mousey.add_cog(Testing(mousey))
