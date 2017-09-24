# -*- coding: utf-8 -*-
from mousey import Cog, commands, Context, Mousey

# this is nowhere near finished, just used to properly test things


class Config(Cog):
    def __init__(self, mousey: Mousey):
        super().__init__(mousey)

        self.configs = {}

    async def get(self, guild_id: int) -> dict:
        """
        Returns a guilds configuration, either from memory or the database.
        If no configuration is found an empty dictionary is found.
        """
        if guild_id == 288369367769677826:  # testing
            config = {
                'logging': {
                    'messages': True
                }, 'commands': {
                    'prefixes': ['~?']
                }
            }
            return config
        return {}

    async def put(self, guild_id: int, config: dict):
        """Save a guild config. This stores it in the database and in memory."""
        self.configs[guild_id] = config


def setup(mousey: Mousey):
    mousey.add_cog(Config(mousey))
