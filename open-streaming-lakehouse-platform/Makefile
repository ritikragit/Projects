.PHONY: kafka-up kafka-down producer deps

kafka-up:
	docker compose -f docker/docker-compose.yml up -d

kafka-down:
	docker compose -f docker/docker-compose.yml down

deps:
	pip install -r services/producer/requirements.txt

producer:
	python services/producer/producer.py
