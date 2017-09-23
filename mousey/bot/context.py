# -*- coding: utf-8 -*-
import discord

from mousey import commands
from mousey.const import DEFAULT_COLOR


class Context(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        mousey = self.bot

        self.mousey = mousey
        self.db = mousey.db
        self.redis = mousey.redis
        self.process = mousey.process
        self.session = mousey.session

    @property
    def color(self):
        """Property returning Mouseys guild color (defined by her roles) or the default Mousey color."""
        color = getattr(self.me, 'color', discord.Color.default())
        return color if color.value != 0 else DEFAULT_COLOR

    async def send(self, content: str=None, *, avoid_bots: bool=True, **kwargs):
        if content is not None:
            if len(content) > 1999:
                pass  # todo: create paste with content

            if avoid_bots:
                content = f'\N{ZERO WIDTH SPACE}{content}' if not content.startswith('`') else content

        return await super().send(content, **kwargs)
