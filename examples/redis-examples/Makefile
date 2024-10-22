# This Makefile requires the following commands to be available:
# * python3.9
# * docker

# Docker Compse options
service=redis-gears

# Docker Compose
bash:
	docker-compose run --user=$(shell id -u) ${service} bash

build:
	docker-compose build

restart:
	docker-compose restart ${service}

run:
	docker-compose up

logs:
	docker-compose logs

# Removes old containers, free's up some space
remove:
	# Try this if this fails: docker rm -f $(docker ps -a -q)
	docker-compose rm --force -v

remove-network:
	docker network rm examples_default || true

stop-redis-cluster:
	docker-compose stop
	@$(MAKE) remove
	@$(MAKE) remove-network

redis-cluster: build run
