FROM python:3.9.15-slim-buster as builder
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
RUN apt-get update
RUN pip3 install poetry==1.2.0
RUN poetry config virtualenvs.create false
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
