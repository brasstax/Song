#!/usr/bin/env python
import logging
from discord.ext import commands
from song.bot_commands import Misc
from song.utilities import twitter
import discord
import asyncio
import argparse
import os
import sys

loop = asyncio.get_event_loop()
parser = argparse.ArgumentParser(description="A twitter discord bot.")

intents = discord.Intents.default()

log_format = "[%(filename)s:%(lineno)s:%(funcName)s() ]%(asctime)s - %(levelname)s - %(message)s"  # noqa
logging.basicConfig(level=logging.INFO, format=log_format)

TOKEN = os.environ.get("DISCORD_TOKEN", None)
if not TOKEN:
    sys.exit("DISCORD_TOKEN environment variable not set.")

COMMAND_PREFIX = os.environ.get("DISCORD_COMMAND_PREFIX", None)
if not COMMAND_PREFIX:
    sys.exit("DISCORD_COMMAND_PREFIX environment variable not set.")

TO_FOLLOW = os.environ.get("SNSCRAPE_TWITTER_USERS", None)
if not TO_FOLLOW:
    sys.exit("SNSCRAPE_TWITTER_USERS environment variable not set.")

DISCORD_NEWS_CHANNEL_ID = os.environ.get("DISCORD_NEWS_CHANNEL_ID", None)
if not DISCORD_NEWS_CHANNEL_ID:
    sys.exit("DISCORD_NEWS_CHANNEL_ID environment variable not set.")

SNSCRAPE_DATABASE_DB = os.environ.get("SNSCRAPE_DATABASE_DB", None)
if not SNSCRAPE_DATABASE_DB:
    sys.exit("SNSCRAPE_DATABASE_DB environment variable not set.")

SNSCRAPE_DATABASE_HOST = os.environ.get("SNSCRAPE_DATABASE_HOST", None)
if not SNSCRAPE_DATABASE_HOST:
    sys.exit("SNSCRAPE_DATABASE_HOST environment variable not set.")

SNSCRAPE_DATABASE_USERNAME = os.environ.get("SNSCRAPE_DATABASE_USERNAME", None)
if not SNSCRAPE_DATABASE_USERNAME:
    sys.exit("SNSCRAPE_DATABASE_USERNAME environment variable not set.")

SNSCRAPE_DATABASE_PASSWORD = os.environ.get("SNSCRAPE_DATABASE_PASSWORD", None)
if not SNSCRAPE_DATABASE_PASSWORD:
    sys.exit("SNSCRAPE_DATABASE_PASSWORD environment variable not set.")

TWITTER_BASE_URL = os.environ.get("TWITTER_BASE_URL", None)
if TWITTER_BASE_URL == "":
    TWITTER_BASE_URL = None

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(COMMAND_PREFIX),
    description="She sees all and she'll snipe you with a bow.",
    case_insensitive=True,
    intents=intents
)
bot.events_channel = DISCORD_NEWS_CHANNEL_ID

setattr(bot, "events_channel", int(DISCORD_NEWS_CHANNEL_ID))

setattr(bot, "is_following", False)

@bot.event
async def on_ready():
    await bot.add_cog(Misc.Commands(bot))
    logging.info(f"Logged in as {bot.user.name} ({bot.user.id})")
    logging.info("------")
    activity = discord.Game(name=f"Discording")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    bot.twitter = twitter.Twitter(
        bot=bot,
        discord_channel_id=DISCORD_NEWS_CHANNEL_ID,
        twitter_usernames=TO_FOLLOW.split(","),
        twitter_database_db=SNSCRAPE_DATABASE_DB,
        twitter_database_host=SNSCRAPE_DATABASE_HOST,
        twitter_database_username=SNSCRAPE_DATABASE_USERNAME,
        twitter_database_password=SNSCRAPE_DATABASE_PASSWORD,
        twitter_base_url=TWITTER_BASE_URL,
    )
    await bot.twitter.follow()


@bot.event
async def on_command_error(ctx, *args, **kwargs):
    warning = args[0]
    guild = ctx.guild
    if guild is None:
        guild = "direct message"
    msg = f"{ctx.author} from {guild} caused an error: {warning}"
    logging.warning(f"message: {msg}")
    pass


try:
    loop.run_until_complete(bot.login(token=TOKEN))
    loop.run_until_complete(bot.connect())
except KeyboardInterrupt:
    logging.info("Logging out. (You might need to ctrl-C twice.)")
    loop.run_until_complete(bot.twitter.client.conn.close())
    loop.run_until_complete(bot.logout())
finally:
    loop.close()
