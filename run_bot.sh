#!/bin/sh

echo "Creating translate files"

pybabel compile -d locales -D picpackbot

echo "Created translate files"

echo "Starting bot"
python3.9 bot_start.py

exec "$@"