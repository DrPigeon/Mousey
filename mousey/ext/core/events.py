# -*- coding: utf-8 -*-
import discord

from mousey import Cog, Mousey


class Events(Cog):
    """Cog to dispatch custom events, lesser the amount of duplicate code in other cogs."""

    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before.nick != after.nick:
            self.mousey.dispatch('nick_update', after, before.nick, after.nick)

        if before.roles != after.roles:
            old = set(before.roles)
            diff = old.symmetric_difference(set(after.roles))

            for role in diff:
                if role in old:
                    self.mousey.dispatch('role_remove', after, role)
                else:
                    self.mousey.dispatch('role_add', after, role)

        if before.name != after.name:
            self.mousey.dispatch('name_change', after, before.name, after.name)

        # not including these as I'm not sure if I'll use them yet~

        # status updates ?
        # game updates

    # role permission changes ?


def setup(mousey: Mousey):
    mousey.add_cog(Events(mousey))
