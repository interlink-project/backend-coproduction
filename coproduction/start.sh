#! /usr/bin/env bash
# https://raw.githubusercontent.com/tiangolo/uvicorn-gunicorn-docker/master/docker-images/gunicorn_conf.py

HOST=${HOST:-0.0.0.0}
PORT=${PORT}
LOG_LEVEL=${LOG_LEVEL:-info}

# Let the DB start
python /app/app/pre_start.py

# Run migrations
# alembic revision --autogenerate -m "Added initial table"
# alembic upgrade head
# echo MIGRATIONS DONE

# Create initial data in DB
python /app/app/initial_data.py

# Start Uvicorn with live reload IF DEVELOPMENT
exec uvicorn --reload --host $HOST --port $PORT --log-level $LOG_LEVEL "app.main:app"

# Start Gunicorn if PRODUCTION 
# exec gunicorn -k "uvicorn.workers.UvicornWorker" -c "app/gunicorn_conf.py" "app.main:app"