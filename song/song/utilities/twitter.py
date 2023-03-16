#!/usr/bin/env python
# twitter.py
# A collection of utilities to get tweet information from
# @Granblue_en.

from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from typing import List, Dict
import logging
import asyncio

class TwitterDatabase:
    @classmethod
    async def create(cls, conn: str):
        self = TwitterDatabase()
        self.conn = AsyncConnectionPool(conn)
        return self
    
    async def get_unread_tweets(self, username: str) -> List[Dict[str, str]]:
        cmd: str = """
        SELECT status_id, date from tweets
        WHERE silva_read is false
        AND username = %s
        ORDER BY date ASC;
        """
        async with self.conn.connection() as db:
            async with db.cursor(row_factory=dict_row) as cur:
                await cur.execute(cmd, (username,), prepare=True)
                tweets: list = []
                async for row in cur:
                    tweet_date = row["date"]
                    tweet_id = row["status_id"]
                    tweets.append(
                        {
                            "tweet_date": tweet_date,
                            "tweet_id": tweet_id
                        }
                    )
        return tweets
    
    async def mark_tweet_read(self, username: str, tweet_id: int):
        cmd: str = """
        UPDATE tweets
        SET silva_read = true
        WHERE username = %s
        AND status_id = %s
        """
        async with self.conn.connection() as db:
            async with db.cursor() as cur:
                await cur.execute(cmd, (username, tweet_id,), prepare=True)
        return
    
    async def check_muted_user(self, username: str):
        """
        Check if a username is ignored.
        """
        cmd: str = """
        SELECT username FROM muted_users
        WHERE username = %s
        """
        async with self.conn.connection() as db:
            async with db.cursor() as cur:
                await cur.execute(cmd, (username,), prepare=True)
                res = await cur.fetchone()
        
        if res:
            return True
        return False
    
    async def mute_twitter_user(self, username: str):
        """
        Mutes a twitter username.
        """
        cmd: str = """
        INSERT INTO muted_users (username)
        VALUES (%s)
        ON CONFLICT username DO NOTHING;
        """
        async with self.conn.connection() as db:
            async with db.cursor() as cur:
                await cur.execute(cmd, (username,))
        return

    async def unmute_twitter_user(self, username: str):
        """
        Unmutes a twitter username.
        """
        cmd: str = """
        DELETE FROM muted_users
        WHERE username = %s;
        """
        async with self.conn.connection() as db:
            async with db.cursor() as cur:
                await cur.execute(cmd, (username,))
        return


class Twitter(object):
    def __init__(
        self,
        bot,
        discord_channel_id: int,
        twitter_database_db: str,
        twitter_database_host: str,
        twitter_database_username: str,
        twitter_database_password: str,
        twitter_usernames: str
    ):
        self.bot = bot
        self.channel_id = int(discord_channel_id)
        self.twitter_connection = f"user={twitter_database_username} password={twitter_database_password} dbname={twitter_database_db} host={twitter_database_host}"
        self.twitter_usernames = twitter_usernames
        self.client = None

    async def follow(self):
        if not self.bot.is_following:
            self.bot.is_following = True
            self.client = await TwitterDatabase.create(self.twitter_connection)
            bot = self.bot
            channel = bot.get_channel(self.channel_id)
            while True:
                for username in self.twitter_usernames:
                    tweets = await self.client.get_unread_tweets(username)
                    for tweet in tweets:
                        sid = tweet["tweet_id"]
                        logging.info(f"@{username}: {sid}")
                        url = f"https://fxtwitter.com/{username}/status/{sid}"
                        logging.info(url)
                        if not await self.client.check_muted_user(username):
                            await channel.send(url)
                        else:
                            logging.info(f"Ignoring {username}")
                        await self.client.mark_tweet_read(username, sid)
                await asyncio.sleep(5)