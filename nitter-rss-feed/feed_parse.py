#!/usr/bin/env python
import os
import signal
import sys
import asyncio
import logging
from datetime import datetime, timezone
import feedparser
from psycopg_pool import AsyncConnectionPool
import psycopg.errors

logging.basicConfig(level=logging.INFO)


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

NITTER_ADDRESS = os.environ.get("NITTER_ADDRESS", None)
if not NITTER_ADDRESS:
    sys.exit("NITTER_ADDRESS environment variable not set.")

conn_str = f"user={SNSCRAPE_DATABASE_USERNAME} password={SNSCRAPE_DATABASE_PASSWORD} dbname={SNSCRAPE_DATABASE_DB} host={SNSCRAPE_DATABASE_HOST}"

async def amain():
  # Block below commented out where I eventually get reply IDs and users working with nitter;
  # for now I'd like to get it to just work again.
  # cmd = """
  # INSERT INTO tweets(username, status_id, date, reply_id, reply_user, silva_read)
  # VALUES ('$username', $status_id, '$date', NULLIF('$reply_id', '0')::bigint, NULLIF('$reply_user', ''), false)
  # ON CONFLICT (username, status_id) DO NOTHING
  # """
  conn = AsyncConnectionPool(conn_str)
  cmd = """
  INSERT INTO tweets(username, status_id, date, silva_read)
  VALUES (%s, %s, %s, false)
  ON CONFLICT (username, status_id) DO NOTHING
  """
  logging.info(f"Now setting up feeds for {TO_FOLLOW}.")
  for username in TO_FOLLOW.split(","):
    feed = feedparser.parse(f"http://{NITTER_ADDRESS}/{username}/with_replies/rss")
    async with conn.connection() as db:
      for entry in feed["entries"]:
        logging.debug(entry)
        tweet_id = int(entry.id.split("/")[-1].split("#")[0])
        published = entry["published"]
        if published == "Mon, 00  0001 00:00:00 GMT":
            # Tweet's valid but is likely NSFW, so an invalid timestamp gets returned by rss. Replace it with "now".
            # TODO: change the logic of this thing so that it's not always now, or check the database first to see
            # when we first published it.
            published = datetime.now(tz=timezone.utc)
        async with db.cursor() as cur:
            logging.info(f"Parse {username} for ID {tweet_id} published {published}, titled {entry['title']}")
            await cur.execute(cmd, (username, tweet_id, published,), prepare=True)

def ask_exit():
    loop = asyncio.get_event_loop()
    for task in asyncio.Task.all_tasks():
        task.cancel()
    loop.stop()

if __name__ == "__main__":
    asyncio.run(amain())
