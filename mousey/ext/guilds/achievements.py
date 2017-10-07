# -*- coding: utf-8 -*-
import inspect

from mousey import Cog, commands, Context, Mousey


class Resources(Cog):
    """
    Resources for achievement hunting communities.

    These commands are hidden due to them not being very useful to most of Mouseys audience.
    """

    @commands.command(hidden=True)
    async def trackers(self, ctx: Context):
        """Show a list of achievement trackers and resources."""
        msg = """
        **Cross Platform**
            <https://completionist.me/> *luchaos*
            <https://exophase.com/> *x3sphere*
            <http://metagamerscore.com/> *primal_r*

        **Steam**
            <https://achievementstats.com/> *ChrissyX*, *munky*
            <http://astats.astats.nl/> *Mytharox*
            <http://steamhunters.com/> *Rudey*
            <https://steamladder.com/> *Terry007*, *Florens*
            <http://steam-tools.net/infograph> *Misteriosm*
            <https://truesteamachievements.com/> *Rich Stone*

        **Retro Achievements**
            <http://retroachievements.org/> *Scott*

        **PSN**
            <http://psnleaderboard.com/> *SkippyCue*
            <http://psnprofiles.com/> *Sly Ripper*
            <http://truetrophies.com/> *Rich Stone*

        **XBOX**
            <http://trueachievements.com/> *Rich Stone*

        **A Collection of Steam Tools**
            <https://steamcommunity.com/sharedfiles/filedetails/?id=451698754> *DKA*
        """

        await ctx.send(inspect.cleandoc(msg))

    @commands.command(hidden=True)
    async def cme(self, ctx: Context):
        """Show an invite link to the completionist.me discord."""
        msg = """
        <https://completionist.me/> is a personal multi platform achievement tracker.

        Our discord guild is a lurker-only tool for exposure of c.me features and development to users.
        Feeds of c.me releases and live achievement updates across steam can be found here, while expansion is planned.

        http://discord.gg/k4rx34T
        """
        await ctx.send(inspect.cleandoc(msg))


def setup(mousey: Mousey):
    mousey.add_cog(Resources(mousey))
