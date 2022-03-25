#!/bin/bash

echo "Migrations update..."

read_var() {
    VAR=$(grep $1 $2 | xargs)
    IFS="=" read -ra VAR <<< "$VAR"
    echo ${VAR[1]}
}

CURRENT_MIGRATION=$(read_var CURRENT_MIGRATION .env)

alembic upgrade $CURRENT_MIGRATION

echo "Creating translate files..."

pybabel compile -d locales -D picpackbot

echo "Starting bot..."

python3.9 bot_start.py

exec "$@"