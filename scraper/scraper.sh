#!/bin/bash
# scraper.sh
# Scrapes twitter using SNScrape for tweets in the environment variable
# SNSCRAPE_TWITTER_USERS (separated by commas)

which snscrape > /dev/null
[[ $? -ne 0 ]] && echo "SNScrape not installed." && exit 1;
which psql > /dev/null
[[ $? -ne 0 ]] && echo "psql not installed." && exit 1;
which zq > /dev/null
[[ $? -ne 0 ]] && echo "zq not installed." && exit 1;
[[ -z ${SNSCRAPE_TWITTER_USERS} ]]  && echo "SNSCRAPE_TWITTER_USERS not set. Set SNSCRAPE_TWITTER_USERS with user handles you want to scrape, separated by comma." && exit 1;
[[ -z ${SNSCRAPE_DATABASE_DB} ]]  && echo "SNSCRAPE_DATABASE_DB not set. Set the name for a postgres database that scraper.sh will use." && exit 1;
[[ -z ${SNSCRAPE_DATABASE_HOST} ]] && echo "SNSCRAPE_DATABASE_HOST not set. Set the host for a postgres host that scraper.sh will use." && exit 1;
[[ -z ${SNSCRAPE_DATABASE_USERNAME} ]] && echo "SNSCRAPE_DATABASE_USERNAME not set. Set the username for a postgres host that scraper.sh will use." && exit 1;
[[ -z ${SNSCRAPE_DATABASE_PASSWORD} ]] && echo "SNSCRAPE_DATABASE_PASSWORD not set. Set the password for a postgres host that scraper.sh will use." && exit 1;
[[ -z ${SNSCRAPE_MAX_RESULTS} ]] && set SNSCRAPE_MAX_RESULTS=10;
echo "Initializing SNScrape for twitter accounts ${SNSCRAPE_TWITTER_USERS}."
echo "SELECT 'CREATE DATABASE ${SNSCRAPE_DATABASE_DB}' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${SNSCRAPE_DATABASE_DB}')\gexec" | psql "user=$SNSCRAPE_DATABASE_USERNAME password=$SNSCRAPE_DATABASE_PASSWORD host=$SNSCRAPE_DATABASE_HOST"
psql "user=$SNSCRAPE_DATABASE_USERNAME password=$SNSCRAPE_DATABASE_PASSWORD host=$SNSCRAPE_DATABASE_HOST dbname=$SNSCRAPE_DATABASE_DB" -c "CREATE TABLE IF NOT EXISTS tweets (username TEXT, status_id BIGINT, date TIMESTAMP WITH TIME ZONE, silva_read BOOLEAN, CONSTRAINT username_status_id UNIQUE (username, status_id))" > /dev/null
psql "user=$SNSCRAPE_DATABASE_USERNAME password=$SNSCRAPE_DATABASE_PASSWORD host=$SNSCRAPE_DATABASE_HOST dbname=$SNSCRAPE_DATABASE_DB" -c "ALTER TABLE tweets ADD COLUMN IF NOT EXISTS hashtags text ARRAY NULL" > /dev/null
psql "user=$SNSCRAPE_DATABASE_USERNAME password=$SNSCRAPE_DATABASE_PASSWORD host=$SNSCRAPE_DATABASE_HOST dbname=$SNSCRAPE_DATABASE_DB" -c "ALTER TABLE tweets ADD COLUMN IF NOT EXISTS reply_id BIGINT NULL" > /dev/null
psql "user=$SNSCRAPE_DATABASE_USERNAME password=$SNSCRAPE_DATABASE_PASSWORD host=$SNSCRAPE_DATABASE_HOST dbname=$SNSCRAPE_DATABASE_DB" -c "ALTER TABLE tweets ADD COLUMN IF NOT EXISTS reply_user TEXT NULL" > /dev/null
psql "user=$SNSCRAPE_DATABASE_USERNAME password=$SNSCRAPE_DATABASE_PASSWORD host=$SNSCRAPE_DATABASE_HOST dbname=$SNSCRAPE_DATABASE_DB" -c "CREATE TABLE IF NOT EXISTS muted_hashtags (id SERIAL PRIMARY KEY, hashtag TEXT)" > /dev/null
psql "user=$SNSCRAPE_DATABASE_USERNAME password=$SNSCRAPE_DATABASE_PASSWORD host=$SNSCRAPE_DATABASE_HOST dbname=$SNSCRAPE_DATABASE_DB" -c "CREATE TABLE IF NOT EXISTS muted_users (username text UNIQUE)" > /dev/null
psql "user=$SNSCRAPE_DATABASE_USERNAME password=$SNSCRAPE_DATABASE_PASSWORD host=$SNSCRAPE_DATABASE_HOST dbname=$SNSCRAPE_DATABASE_DB" -c "CREATE TABLE IF NOT EXISTS settings(id SERIAL PRIMARY KEY, name TEXT, value TEXT)" > /dev/null
IFS=',' read -ra USERS <<< $SNSCRAPE_TWITTER_USERS
echo "Now scraping. Press Ctrl-C to exit."
trap "exit" SIGTERM
trap "exit" SIGINT
while true; do
  for user in "${USERS[@]}"; do
    echo "Scraping $user"
    IFS=' ' mapfile -t tweets < <(snscrape --max-results $SNSCRAPE_MAX_RESULTS --retry 3 --jsonl twitter-search "from:$user include:nativeretweets")
#    IFS=' ' mapfile -t -O "${#tweets[@]}" tweets < <(snscrape --max-results $SNSCRAPE_MAX_RESULTS --retry 3 --jsonl twitter-profile $user)
    for tweet in "${tweets[@]}"; do
      username=$(echo $tweet | zq -f zson 'yield user.username' - | sed s/\"//g)
      status_id=$(echo $tweet | zq -f zson 'yield id' -)
      reply_id=$(echo $tweet | zq -f zson 'yield inReplyToTweetId' -)
      [[ $reply_id == 'null' ]] && reply_id=0
      reply_user=$(echo $tweet | zq -f zson 'yield inReplyToUser.username' - | sed s/\"//g)
      [[ $reply_user == 'error("missing")' ]] && reply_user=''
      [[ $reply_user == 'error(missing)' ]] && reply_user=''
      date=$(echo $tweet | zq -f zson 'yield date' -)
      psql "user=$SNSCRAPE_DATABASE_USERNAME password=$SNSCRAPE_DATABASE_PASSWORD host=$SNSCRAPE_DATABASE_HOST dbname=$SNSCRAPE_DATABASE_DB" -c "INSERT INTO tweets(username, status_id, date, reply_id, reply_user, silva_read) VALUES ('$username', $status_id, '$date', NULLIF('$reply_id', '0')::bigint, NULLIF('$reply_user', ''), false) ON CONFLICT (username, status_id) DO NOTHING" > /dev/null
    done
  done
  sleep 2
done
