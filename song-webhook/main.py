#!/usr/bin/env python
import httpx as requests
from song_webhook.utilities import twitter
import logging
import asyncio
import argparse
import os
import sys

loop = asyncio.get_event_loop()
client = requests.AsyncClient()
parser = argparse.ArgumentParser(description="A twitter discord bot.")

log_format = "[%(filename)s:%(lineno)s:%(funcName)s() ]%(asctime)s - %(levelname)s - %(message)s"  # noqa
logging.basicConfig(level=logging.INFO, format=log_format)

TO_FOLLOW = os.environ.get("SNSCRAPE_TWITTER_USERS", None)
if not TO_FOLLOW:
    sys.exit("SNSCRAPE_TWITTER_USERS environment variable not set.")

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

DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK", None)
if not DISCORD_WEBHOOK:
    sys.exit("DISCORD_WEBHOOK environment variable not set.")

tweeter = twitter.Twitter(
    client,
    twitter_database_db=SNSCRAPE_DATABASE_DB,
    twitter_database_host=SNSCRAPE_DATABASE_HOST,
    twitter_database_username=SNSCRAPE_DATABASE_USERNAME,
    twitter_database_password=SNSCRAPE_DATABASE_PASSWORD,
    twitter_usernames=TO_FOLLOW,
    discord_webhook=DISCORD_WEBHOOK,
)


def main():
    try:
        logging.info("Now starting.")
        loop.run_until_complete(tweeter.follow())
    except KeyboardInterrupt:
        logging.info("Logging out. (You might need to ctrl-C twice.)")
        loop.run_until_complete(client.aclose())
        loop.stop()
    finally:
        loop.close()


if __name__ == "__main__":
    main()
