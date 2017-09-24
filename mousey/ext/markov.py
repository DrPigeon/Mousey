# -*- coding: utf-8 -*-
import asyncio
import functools
import time

import discord
import markovify

from mousey import Cog, commands, Context, Mousey
from mousey.const import DENY_EMOJI
from mousey.utils import clean_text, MemberOrChannel


class NoMessages(Exception):
    """Exception raised if the target can't be used in markov."""
    def __init__(self, message: str):
        self.message = message


class Markov(Cog):
    """Markov chains of members and channels."""

    def __init__(self, mousey: Mousey):
        super().__init__(mousey)

        self.models = {}
        self.limiter = asyncio.Semaphore()

    def __unload(self):
        for target_key in list(self.models.keys()):
            del self.models[target_key]

    @commands.command(typing=True)
    @commands.guild_only()
    async def markov(self, ctx: Context, *, target: MemberOrChannel=None):
        """
        Generate a sentence of a users/channels previous messages.

        This is supposed to generate funny messages which are similar to what is frequently said.
        Message logging needs to be enabled in the guild.
        This is due to it being hard to fetch enough messages a single user sent using message history.
        """
        target = target or ctx.author

        # check if message logging is even enabled in this guild
        config = await self.mousey.get_config(ctx.guild)

        if config.get('logging', {}).get('messages', False) is False:
            return await ctx.send(f'{DENY_EMOJI} Markov can\'t be used as message logging is not enabled.')

        try:
            model = await self.get_model(ctx.guild, target)
        except NoMessages as e:
            return await ctx.send(e.message)

        make_sentence = functools.partial(model.make_sentence, tries=50)
        sentence = await self.loop.run_in_executor(None, make_sentence)

        if sentence is not None:
            message = clean_text(ctx.channel, sentence)
            await ctx.send(message)
        else:
            await ctx.send(f'{DENY_EMOJI} Couldn\'t generate sentence! Target does not have enough messages yet.')

    async def get_model(self, guild, target):
        """
        Generate a markov model of the specified user or channel.

        Parameters
        ----------
        guild : discord.Guild
            The guild to fetch channels from
        target : Union[discord.Member, discord.TextChannel]
            The user or channel to fetch messages from.

        Returns
        -------
        markovify.NewlineText
            The generated markov model
        """
        async with self.limiter:
            target_key = f'{guild.id}:{target.id}'

            # see if a generated model exists
            if target_key in self.models:
                now = time.monotonic()
                self.models[target_key][0] = now

                return self.models[target_key][1]

            messages = await self.get_messages(guild, target)

            def build_model(*msgs: str) -> markovify.NewlineText:
                return markovify.NewlineText('\n'.join(msgs))

            make_model = functools.partial(build_model, *messages)
            model = await self.loop.run_in_executor(None, make_model)

            now = time.monotonic()
            self.models[target_key] = [now, model]

            return model

    async def get_messages(self, guild, target):
        """
        Get message content from public guild channels and optionally specific users.

        Parameters
        ----------
        guild : discord.Guild
            The guild to fetch messages from
        target : Union[discord.Member, discord.TextChannel]
            The channel or member to fetch messages from

        Returns
        -------
        List[str]
            The messages the target sent in the specified channels
        """
        if isinstance(target, discord.TextChannel):
            channels = [target]
        else:
            channels = guild.text_channels
        public_channels = []

        for channel in channels:
            if not await self.channel_is_private(channel):
                continue

            public_channels.append(channel.id)

        # no public channels
        if not public_channels:
            raise NoMessages(f'{DENY_EMOJI} No public target channel could be found. Can\'t generate sentence.')

        async with self.db.acquire() as conn:
            if isinstance(target, discord.Member):
                query = 'SELECT content FROM messages WHERE channel_id=ANY($1) AND author_id = $2 LIMIT 10000'
                results = await conn.fetch(query, public_channels, target.id)
            else:
                query = 'SELECT content FROM messages WHERE channel_id=ANY($1) LIMIT 10000'
                results = await conn.fetch(query, public_channels)

        return [x['content'] for x in results]

    async def channel_is_private(self, channel):
        """
        Returns whether a channel has more than 25% of guild population in it.

        Parameters
        ----------
        channel : discord.TextChannel
            The channel to calculate user count of

        Returns
        -------
        bool
            Whether the channel is public or not
        """
        key = f'mousey:markov_channels:{channel.id}'
        with await self.redis as conn:
            result = await conn.get(key)

        if result is not None:
            return bool(int(result))

        is_private = len(channel.members) > 0.25 * channel.guild.member_count

        # save result for a day as calculating takes a while on big guilds
        with await self.redis as conn:
            await conn.set(key, int(is_private), expire=60 * 60 * 24)

        return is_private

    @commands.schedule(60)
    async def markov_cleaner(self):
        """Deletes models which haven't been used in the past 10 minutes."""
        now = time.monotonic()

        for target_key in list(self.models.keys()):
            last_used = self.models[target_key][0]

            if now - 60 * 10 < last_used:
                continue

            del self.models[target_key]


def setup(mousey: Mousey):
    mousey.add_cog(Markov(mousey))
