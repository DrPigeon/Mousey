# -*- coding: utf-8 -*-
import enum

from discord.ext.commands.converter import *

from .context import Context
from .core import RecalledArgument
from .errors import BadArgument


__all__ = (
    'CategoryChannelConverter',
    'clean_content',
    'ColourConverter',
    'Converter',
    'EmojiConverter',
    'EnumConverter',
    'GameConverter',
    'IDConverter',
    'InviteConverter',
    'MemberConverter',
    'Optional',
    'RoleConverter',
    'TextChannelConverter',
    'UserConverter',
    'VoiceChannelConverter',
)


class Optional(Converter):
    """
    Class which takes a Converter as an argument and makes it an optional argument by returning nothing
    on conversion failure.
    If a default is set for this parameter it will be used, otherwise the typical MissingRequiredArgument is raised.
    """
    def __init__(self, converter):
        self.converter = converter

    async def convert(self, ctx, argument):
        try:
            return await ctx.command.do_conversion(ctx, self.converter, argument)
        except (BadArgument, ValueError, TypeError):
            return RecalledArgument(argument)


# almost copied from https://github.com/slice/dogbot/blob/master/dog/core/utils/enum.py
class EnumConverter:
    """
    A class that when subclassed, turns an :class:`enum.Enum` into a converter that functions by looking up
    enum values' names when passed as arguments.
    """
    @classmethod
    async def convert(cls: enum.Enum, ctx: Context, arg: str):
        try:
            if arg not in [e.name for e in cls]:
                return cls[arg.upper()]
            else:
                return cls[arg]
        except KeyError:  # value in enum not found
            valid_keys = ', '.join('{}'.format(num.name.lower()) for num in list(cls))
            raise BadArgument(f'Choose one of these options: {valid_keys}')
