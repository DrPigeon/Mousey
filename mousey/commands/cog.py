# -*- coding: utf-8 -*-
import asyncio
import inspect


class Cog:
    def __init__(self, bot):
        self.bot = bot
        self.loop = bot.loop

        # start all scheduled tasks
        self._scheduled_tasks = []
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            schedule = getattr(method, '__schedule', None)
            if schedule is None:
                continue

            self._start_scheduled(method, **schedule)

    def _start_scheduled(self, method, interval: int, wait_until_ready: bool):
        """Repeatedly runs a method on a specified interval."""
        async def run_method():
            if wait_until_ready:
                await self.bot.wait_until_ready()

            while not self.bot.is_closed():
                await asyncio.sleep(interval)

                try:
                    await method()
                except Exception as e:
                    self.bot.dispatch('scheduled_error', method.__name__, e)

        task = self.loop.create_task(run_method())
        self._scheduled_tasks.append(task)
