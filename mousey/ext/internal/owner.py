# -*- coding: utf-8 -*-
import asyncio
import contextlib
import inspect
import io
import textwrap
import traceback

import asyncpg
import discord

from mousey.const import DENY_EMOJI
from mousey import Cog, commands, Context, Mousey
from mousey.utils import Table, Timer


def no_codeblock(text: str) -> str:
    """
    Removes codeblocks (grave accents), python and sql syntax highlight indicators from a text if present.

    .. note:: only the start of a string is checked, the text is allowed to have grave accents in the middle
    """
    if text.startswith('```'):
        text = text[3:-3]

        if text.startswith(('py', 'sql')):
            # cut off the first line as this removes the highlight indicator regardless of length
            text = '\n'.join(text.split('\n')[1:])

    if text.startswith('`'):
        text = text[1:-1]

    return text


async def run_subprocess(cmd: str) -> str:
    """Runs a subprocess and returns the output."""
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    results = await process.communicate()
    return ''.join(x.decode('utf-8') for x in results)


class Owner(Cog):
    """Commands to make running Mousey easier and make the experience more pleasant."""

    async def __local_check(self, ctx: Context):
        return await self.mousey.is_owner(ctx.author)

    @commands.command(aliases=['logout'])
    async def restart(self, ctx: Context):
        """Restart Mousey."""
        await ctx.ok()
        await self.mousey.logout()

    @commands.command(name='sh')
    async def shell(self, ctx: commands.Context, *, cmd: no_codeblock):
        """Run a subprocess using shell."""
        async with ctx.typing():
            result = await run_subprocess(cmd)
        await ctx.send(f'```{result}```')

    @commands.command()
    async def update(self, ctx: commands.Context):
        """Update from git."""
        async with ctx.typing():
            result = await run_subprocess('git pull')
        await ctx.send(f'```{result}```')

    @commands.command()
    async def delete(self, ctx: commands.Context, user_id: int):
        """
        Permanently delete any saved data about a discord user.
        The discord API TOS requires bot developers to delete user data on request.

        The full API TOS can be found at https://discordapp.com/developers/docs/legal
        """
        raise NotImplementedError()

    @commands.command(typing=True)
    async def sql(self, ctx: commands.Context, *, statement: no_codeblock):
        """Execute SQL."""
        # this is probably not the ideal solution
        if 'select' in statement.lower():
            coro = self.db.fetch
        else:
            coro = self.db.execute

        try:
            with Timer() as t:
                result = await coro(statement)

        except asyncpg.PostgresError as e:
            return await ctx.send(f'{DENY_EMOJI} Failed to execute! {type(e).__name__}: {e}')

        # execute returns the status as a string
        if isinstance(result, str):
            return await ctx.send(f'```py\n{result}```took {t.duration:.3f}ms')

        if not result:
            return await ctx.send(f'no results, took {t.duration:.3f}ms')

        # render output of statement
        columns = list(result[0].keys())
        table = Table(*columns)

        for row in result:
            values = [str(x) for x in row]
            table.add_row(*values)

        rendered = await table.render(self.loop)

        # properly emulate the psql console
        rows = len(result)
        rows = f'({rows} row{"s" if rows > 1 else ""})'

        await ctx.send(f'```py\n{rendered}\n{rows}```took {t.duration:.3f}ms')

    @commands.command(name='eval')
    async def eval_(self, ctx: commands.Context, *, code: no_codeblock):
        """Evaluate code."""
        env = {
            'author': ctx.author,
            'bot': self.mousey,
            'channel': ctx.channel,
            'ctx': ctx,
            'db': self.db,
            'discord': discord,
            'guild': ctx.guild,
            'loop': self.loop,
            'me': ctx.author,
            'message': ctx.message,
            'mousey': self.mousey,
            'redis': self.redis,
        }

        try:
            result = eval(code, env)
            if inspect.isawaitable(result):
                result = await result
        except Exception as e:
            result = str(e)
        else:
            if not isinstance(result, str):
                result = repr(result) if result is not None else 'no result'

        await ctx.send(f'```py\n{result}```')

    @commands.command(name='exec', typing=True)
    async def exec_(self, ctx: commands.Context, *, code: no_codeblock):
        """Run code."""
        env = {
            'author': ctx.author,
            'bot': self.mousey,
            'channel': ctx.channel,
            'ctx': ctx,
            'db': self.db,
            'discord': discord,
            'guild': ctx.guild,
            'loop': self.loop,
            'me': ctx.author,
            'message': ctx.message,
            'mousey': self.mousey,
            'redis': self.redis,
        }

        stdout = io.StringIO()

        code = textwrap.indent(code, '    ')
        func = f"async def cheese():\n{code}"

        try:
            with contextlib.redirect_stdout(stdout):
                exec(func, env)
                result = await env['cheese']()

            if result is not None:
                if not isinstance(result, str):
                    result = repr(result)

                await ctx.send(f'```py\n{result}```')

            output = stdout.getvalue()
            if output != '':
                await ctx.send(f'```py\n{output}```')

            await ctx.ok()
        except Exception:
            trace = traceback.format_exc(limit=10)
            await ctx.send(f'```py\n{trace}```')


def setup(mousey: Mousey):
    mousey.add_cog(Owner(mousey))
