# This Makefile requires the following commands to be available:
# * python3.9
# * docker

# Docker Compse options
service=kafka
worker=app
partitions=1
replication-factor=1


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

stop-kafka-cluster:
	docker-compose stop
	@$(MAKE) remove
	@$(MAKE) remove-network

kafka-cluster: build run

# Kafka related
list-topics:
	docker-compose exec kafka kafka-topics --list --bootstrap-server kafka:9092

create-topic:
	docker-compose exec kafka kafka-topics --create  --if-not-exists \
		--bootstrap-server kafka:9092 \ --replication-factor ${replication-factor} --partitions ${partitions} --topic ${topic-name}

create-example-topics:
	@$(MAKE) create-topic topic-name="my-topic"
