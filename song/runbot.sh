#!/bin/bash
cd "$(dirname "$0")"
until /usr/bin/env python3 bot.py; do
  echo "Song crashed with an exit code $?. Respawning..." >&2
  sleep 60
done
