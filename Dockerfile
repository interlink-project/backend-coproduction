FROM python:3.9-slim-buster as os-base
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
RUN apt-get update
# allow git clone of interlinkers-data repository on seed
RUN apt-get install -y curl git

FROM os-base as poetry-base
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
ENV PATH="/root/.poetry/bin:$PATH"
RUN poetry config virtualenvs.create false
RUN apt-get remove -y curl

FROM poetry-base as builder
WORKDIR /app/
# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./coproduction/pyproject.toml ./coproduction/poetry.lock* /app/
COPY ./coproduction /app
RUN chmod +x /app/start-dev.sh
RUN chmod +x /app/start-prod.sh
RUN chmod +x /app/worker-start.sh
ENV PYTHONPATH=/app

# this will only matter for celery
ENV C_FORCE_ROOT=1

FROM builder as dev
RUN poetry install --no-root
# FOR DATABASE DIAGRAM GENERATION
RUN apt-get update \
  && apt-get install -y --no-install-recommends graphviz \
  && rm -rf /var/lib/apt/lists/*
CMD ["bash", "./start-dev.sh"]

FROM builder as prod
RUN poetry install --no-root --no-dev
CMD ["bash", "./start-prod.sh"]
