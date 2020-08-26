# This Makefile requires the following commands to be available:
# * python3.7
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
	docker network rm de-selfcare-esim_default || true

stop-kafka-cluster:
	docker-compose stop
	@$(MAKE) remove
	@$(MAKE) remove-network
	rm -rf de-selfcare-esim-data || true

kafka-cluster: build run

# Kafka related
list-topics:
	docker-compose exec kafka kafka-topics --list --zookeeper zookeeper:32181

create-topic:
	docker-compose exec kafka kafka-topics --create --zookeeper zookeeper:32181 --replication-factor ${replication-factor} --partitions ${partitions} --topic ${topic-name}


start-app:
	@$(MAKE) create-topic topic-name="my_topic" || true
	python aiokafka_example.py
