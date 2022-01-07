SHELL := /bin/bash

.PHONY: down
down: ## Stops all containers and removes volumes
	docker-compose -f docker-compose.yml -f docker-compose.integrated.yml -f docker-compose.solodev.yml down --volumes --remove-orphans

.PHONY: devbuild
build: ## Build development containers
	docker-compose -f docker-compose.yml -f docker-compose.solodev.yml build

.PHONY: prodbuild
prodbuild: ## Build production containers
	docker-compose -f docker-compose.yml build

.PHONY: solodev
dev: down ## Start solo development containers
	docker-compose -f docker-compose.yml -f docker-compose.solodev.yml up -d

.PHONY: up
up: down ## Start integrated development containers
	docker-compose -f docker-compose.yml -f docker-compose.integrated.yml up -d

.PHONY: prod
prod: down ## Start production containers
	docker-compose -f docker-compose.yml up

.PHONY: seed
seed: ## Seed data
	docker-compose exec coproduction python /app/app/initial_data.py
