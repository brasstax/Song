#!/usr/bin/env python
import logging
from discord.ext import commands

class Commands(commands.Cog, name="Misc. commands"):
    def __init__(self, bot):
        self.bot = bot
        logging.info("Misc commands initialized.")

    @commands.command(name="info", aliases=["blame", "github", "credits"])
    async def info(self, ctx):
        """
        Outputs running info about this bot.
        """
        guild = ctx.guild if ctx.guild else "a direct message"
        logging.info(f"blame requested by {ctx.author} in {guild}.")
        app_info = await self.bot.application_info()
        msg = Embed(
            title="Song (https://github.com/brasstax/silva)",
            url="https://github.com/brasstax/song",
            color=Colour.teal(),
        )
        msg.set_author(
            name="Song",
            url="https://github.com/brasstax/song",
            icon_url=app_info.icon_url,
        )
        msg.add_field(name="Author", value=app_info.owner, inline=False)
        await ctx.send(embed=msg)