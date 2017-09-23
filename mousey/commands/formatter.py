# -*- coding: utf-8 -*-
from discord.ext import commands


class HelpFormatter(commands.HelpFormatter):
    @property
    def clean_prefix(self):
        """The cleaned up invoke prefix. i.e. mentions are ``@name`` instead of ``<@id>``."""
        user = self.context.me
        prefix = self.context.prefix

        # the default clean prefix does not handle the bot having a nickname
        # this replaces it with the original username, another option would be to use the @nickname format
        return prefix.replace(user.mention, f'@{user}').replace(f'<@!{user.id}>', f'@{user}')
