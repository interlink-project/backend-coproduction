SHELL := /bin/bash

.PHONY: down
down: ## Stops all containers and removes volumes
	docker-compose -f docker-compose.yml -f docker-compose.integrated.yml -f docker-compose.solodev.yml down --volumes --remove-orphans

.PHONY: up
up: down ## Run containers (restarts them if already running)
	docker-compose -f docker-compose.yml -f docker-compose.solodev.yml up -d

.PHONY: build
build: ## Build containers
	docker-compose -f docker-compose.yml -f docker-compose.solodev.yml build

.PHONY: upb
upb: down build up ## Build and run containers
