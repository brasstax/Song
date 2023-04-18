# Song
A Discord bot primarily used for a personal project.
Uses `discord.py`.
Like [Silva](https://github.com/brasstax/Silva), but just does twitter instead, without using Twitter's API.

SNScrape scrapes tweets for a user into a postgres database, and then Song goes through the tweets as they come in
and posts them to a discord channel of your choice.

# Running
Copy `docker-compose.sample.yml` to `docker-compose.yml` and fill out the blanks, then run `docker compose up`.

# Logging
All command invocations log to stdout. Any tweets that come in also get logged into stdout as well.
