# -*- coding: utf-8 -*-
import importlib
import logging
import sys

from mousey import Cog, commands, Context, Mousey
from mousey.const import DENY_EMOJI, EXT_PATH


log = logging.getLogger(__name__)
EXT_BASE = EXT_PATH.replace('/', '.')


class Reload(Cog):
    """Cog to reload extensions. This is to avoid the reloading of the extension with the reload command failing."""

    async def __local_check(self, ctx: Context):
        return await ctx.bot.is_owner(ctx.author)

    @commands.command()
    async def load(self, ctx: Context, *, extension: str):
        """Load an extension."""
        name = f'{EXT_BASE}{extension}'

        try:
            self.mousey.load_extension(name)
        except Exception as e:
            msg = f'failed to load {name}: {type(e).__name__} - {e}'
            log.warning(msg)
            await ctx.send(f'{DENY_EMOJI} {msg}')
        else:
            log.info(f'loaded {name}')
            await ctx.ok()

    @commands.group()
    async def reload(self, ctx: Context, *, extension: str):
        """Reload an extension."""
        name = f'{EXT_BASE}{extension}'

        try:
            self.mousey.reload_extension(name)
        except Exception as e:
            msg = f'failed to reload {name}: {type(e).__name__} - {e}'
            log.warning(msg)
            await ctx.send(f'{DENY_EMOJI} {msg}')
        else:
            log.info(f'reloaded {name}')
            await ctx.ok()

    @reload.command(aliases=['all'])
    async def full(self, ctx: Context):
        """Reloads all extensions."""
        log.info('reloading all extensions')

        extensions = self.mousey.extensions.copy()
        for name in extensions:
            try:
                self.mousey.reload_extension(name)
            except Exception as e:
                msg = f'failed to reload {name}: {type(e).__name__} - {e}'
                log.warning(msg)
                await ctx.send(f'{DENY_EMOJI} {msg}')

        await ctx.ok()

    @commands.command()
    async def unload(self, ctx: Context, *, extension: str):
        """Unload an extension."""
        name = f'{EXT_BASE}{extension}'

        try:
            self.mousey.unload_extension(name)
        except Exception as e:
            msg = f'failed to unload {name}: {type(e).__name__} - {e}'
            log.warning(msg)
            await ctx.send(f'{DENY_EMOJI} {msg}')
        else:
            log.info(f'unloaded {name}')
            await ctx.ok()


def setup(mousey: Mousey):
    mousey.add_cog(Reload(mousey))
