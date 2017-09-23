# -*- coding: utf-8 -*-
import enum
from typing import Generator

from discord.ext.commands.converter import *
from discord.ext.commands.view import quoted_word, StringView

from .context import Context
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
    'RoleConverter',
    'StringView',
    'TextChannelConverter',
    'UserConverter',
    'ViewConverter',
    'VoiceChannelConverter',
)


class ViewConverter:
    """
    Converters inheriting from this class do not get the argument passed as a string, but rather the StringView.

    This makes it convenient to write multi word converters, as the words method allows getting one quoted
    word from the view at a time.
    """

    @staticmethod
    def words(view: StringView) -> Generator[str, None, None]:
        """Yields each argument from a given StringView."""
        while not view.eof:
            view.skip_ws()
            yield quoted_word(view)


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
