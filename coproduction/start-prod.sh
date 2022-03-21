#! /usr/bin/env bash
# https://raw.githubusercontent.com/tiangolo/uvicorn-gunicorn-docker/master/docker-images/gunicorn_conf.py

HOST=${HOST:-0.0.0.0}
PORT=${PORT}
LOG_LEVEL=${LOG_LEVEL:-info}

mkdir -p /app/static/coproductionprocesses || true
mkdir -p /app/static/teams || true

# Let the DB start
python /app/app/pre_start.py

sleep 5

# Run migrations
alembic revision --autogenerate -m "Added initial table"
alembic upgrade head

echo MIGRATIONS DONE

exec gunicorn -k "uvicorn.workers.UvicornWorker" -c "gunicorn_conf.py" "app.main:app"
