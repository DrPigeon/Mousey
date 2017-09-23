# -*- coding: utf-8 -*-
from mousey import commands, Context


def is_admin():
    """Decorator which adds a bot admin check to a command."""
    async def predicate(ctx: Context) -> bool:
        return await ctx.mousey.is_admin(ctx.author)
    return commands.check(predicate)
