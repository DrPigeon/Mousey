# -*- coding: utf-8 -*-
import discord
from discord.ext import commands


class Context(commands.Context):
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
