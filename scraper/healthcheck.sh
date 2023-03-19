#!/bin/bash
# healthcheck.sh

which psql > /dev/null
[[ $? -ne 0 ]] && echo "psql not installed." && exit 1;

PGPASSWORD=$SNSCRAPE_DATABASE_PASSWORD psql -U $SNSCRAPE_DATABASE_USERNAME -h $SNSCRAPE_DATABASE_HOST $SNSCRAPE_DATABASE_DB -c "select version" > /dev/null > 2&>1