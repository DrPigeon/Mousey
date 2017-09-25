# -*- coding: utf-8 -*-
import datetime
import inspect
import platform
import time

import discord

from mousey import Cog, commands, Context, Mousey, utils


class Stats(Cog):
    """Statistics about Mousey."""

    @commands.command(aliases=['ping'])
    async def rtt(self, ctx: Context):
        """
        Shows Mouseys http and websocket latency.

        rtt: time to send a message (round trip time, http latency)
        ws:  delta between last HEARTBEAT and HEARTBEAT ACK (websocket)
        gw:  difference between message timestamp and arrival (gateway lag)

        gw may be slightly inaccurate due to discords and the servers clock not being in sync.
        """
        arrival = datetime.datetime.utcnow()

        before = time.perf_counter()
        msg = await ctx.send('...')
        after = time.perf_counter()

        rtt = (after - before) * 1000
        ws = self.mousey.latency * 1000
        gw = (arrival - ctx.message.created_at).total_seconds() * 1000

        await msg.edit(content=f'Pong! rtt: {rtt:.3f}ms, ws: {ws:.3f}ms, gw: {gw:.3f}ms')

    @commands.command()
    async def uptime(self, ctx: Context):
        """Shows Mouseys uptime."""
        delta = utils.human_delta(self.mousey.uptime)
        await ctx.send(f'I\'ve been running for {delta}.')

    @commands.command()
    async def about(self, ctx: Context):
        """Shows some information and helpful links around Mousey."""
        description = """
        Mousey is FrostLuma#0005s personal discord bot with a focus on powerful moderation and utility commands.
        For help, questions and updates join the [support guild](https://discord.gg/SjBdRr7)!
        """
        embed = discord.Embed(description=inspect.cleandoc(description), color=ctx.color)
        embed.set_author(name='Mousey', icon_url=self.mousey.user.avatar_url)
        embed.set_footer(text='')

        embed.add_field(name='Python Version', value=platform.python_version())
        embed.add_field(name='Discord.py Version', value=discord.__version__)
        embed.add_field(name='\u200b', value='\u200b')

        delta = utils.human_delta(self.mousey.uptime)

        process = self.mousey.process
        with process.oneshot():
            cpu_percent = process.cpu_percent()
            memory_bytes = process.memory_full_info().rss

        memory_mib = memory_bytes / (1024 * 1024)  # 1 MiB in bytes

        embed.add_field(name='Uptime', value=delta)
        embed.add_field(name='Cpu Usage', value=f"{cpu_percent}%")
        embed.add_field(name='Memory Usage', value=f"{memory_mib:.2f}MiB")

        await ctx.send(embed=embed)

    @commands.command(name='commandstats', aliases=['cstats'], disabled=True, hidden=True)
    async def command_stats(self, ctx: Context):
        """Shows command usage statistics."""
        pass  # todo

    @commands.command(name='botstats', aliases=['bstats'],  disabled=True, hidden=True)
    async def mousey_stats(self, ctx: Context):
        """Shows detailed statistics about Mousey."""
        pass  # todo


def setup(mousey: Mousey):
    mousey.add_cog(Stats(mousey))
