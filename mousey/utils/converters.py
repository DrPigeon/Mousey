# -*- coding: utf-8 -*-
from mousey import commands, Context


__all__ = (
    'MemberOrChannel',
)


class MemberOrChannel(commands.Converter):
    """Converter which attempts to convert to a member or channel."""

    async def convert(self, ctx: Context, argument: str):
        try:
            return await commands.MemberConverter().convert(ctx, argument)
        except commands.BadArgument:
            pass

        try:
            return await commands.TextChannelConverter().convert(ctx, argument)
        except commands.BadArgument:
            pass

        raise commands.BadArgument(f'Member or Channel "{argument}" not found.')
