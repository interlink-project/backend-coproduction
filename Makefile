SHELL := /bin/bash

.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: clean
clean: ## Cleans
	find ./app -type d -name __pycache__ -exec rm -r {} \+

.PHONY: down
down: ## Stops all containers and removes volumes
	docker-compose down --remove-orphans
	
#######################
## BUILD IMAGES
#######################

.PHONY: build
build: ## Builds development containers
	docker-compose build

#######################
## RUN CONTAINERS
#######################

.PHONY: integrated
integrated: down ## Starts integrated development containers
	docker network create traefik-public || true
	docker-compose up -d

#######################
## RUN TESTS
#######################

.PHONY: tests
tests: ## Starts test container
	#docker-compose exec coproduction pytest --cov=app --cov-report=term-missing app/tests
	docker-compose exec -T coproduction pytest app/tests

.PHONY: testing
testing: build solo tests down ## Builds containers, runs them, runs test container and deletes all containers

#######################
## DATABASE SEEDING
#######################

.PHONY: migrations
migrations: ## Seed data
	@[ "${message}" ] || ( echo ">> message not specified (make migrations message='your message'"; exit 1 )
	docker-compose exec coproduction alembic revision --autogenerate -m $(message)

.PHONY: applymigrations
applymigrations: ## Seed data
	docker-compose exec coproduction alembic upgrade head

.PHONY: seed
seed: ## Seed data
	docker-compose exec coproduction python /app/app/pre_start.py
	docker-compose exec coproduction ./seed.sh

.PHONY: kpis
kpis: ## Show kpis
	docker-compose exec coproduction python /app/app/kpis.py
