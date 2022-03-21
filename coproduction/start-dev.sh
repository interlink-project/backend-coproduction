#! /usr/bin/env bash
# https://raw.githubusercontent.com/tiangolo/uvicorn-gunicorn-docker/master/docker-images/gunicorn_conf.py

HOST=${HOST:-0.0.0.0}
PORT=${PORT}
LOG_LEVEL=${LOG_LEVEL:-info}

mkdir -p /app/static/coproductionprocesses || true

# Let the DB start
python /app/app/pre_start.py

# If not migrations, create models in DB automatically without migrations
python /app/app/create_models.py

# Start Uvicorn with live reload
exec uvicorn --reload --host $HOST --port $PORT --log-level $LOG_LEVEL "app.main:app"