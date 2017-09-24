# -*- coding: utf-8 -*-
import discord
from discord.ext import commands


class Context(commands.Context):
    async def send(self, content: str=None, *, avoid_bots: bool=True, **kwargs):
        if content is not None and avoid_bots:
            # don't add a zws if the message is a codeblock as this adds a newline at the start of the message
            content = f'\N{ZERO WIDTH SPACE}{content}' if not content.startswith('`') else content
        return await super().send(content, **kwargs)

    async def ok(self):
        """Adds an approval emoji to the current message or sends it to the current channel."""
        if self.channel.permissions_for(self.me).external_emojis and self.bot.approve_emoji is not None:
            emoji = self.bot.get_emoji(self.bot.approve_emoji)
        else:
            emoji = '\N{WHITE HEAVY CHECK MARK}'

        if self.channel.permissions_for(self.me).add_reactions:
            action = self.message.add_reaction(emoji)
        else:
            action = self.send(emoji)

        try:
            await action
        except discord.HTTPException:
            pass  # /shrug
