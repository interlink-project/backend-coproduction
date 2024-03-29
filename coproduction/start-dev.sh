#! /usr/bin/env bash
# https://raw.githubusercontent.com/tiangolo/uvicorn-gunicorn-docker/master/docker-images/gunicorn_conf.py

HOST=${HOST:-0.0.0.0}
PORT=${PORT}
LOG_LEVEL=${LOG_LEVEL:-info}

mkdir -p /app/static/coproductionprocesses || true
mkdir -p /app/static/teams || true
mkdir -p /app/static/assets || true
mkdir -p /app/static/organizations || true
mkdir -p /app/static/notifications || true
mkdir -p /app/static/stories || true

# Let the DB start
python /app/app/pre_start.py

# Execute only-dev stuff
python /app/app/development.py

# Changes in database are managed by alembic. CHECK MAKEFILE make migrations message="message"

# Start Uvicorn with live reload
exec uvicorn --reload --host $HOST --port $PORT --log-level $LOG_LEVEL "app.main:app"