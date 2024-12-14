
.EXPORT_ALL_VARIABLES:

FLASK_APP ?= main.py
FLASK_ENV ?= development
FLASK_DEBUG ?= 0


run:
	python main.py

build:
	./scripts/build.sh

test:
	# curl -X POST -H "Content-Type: application/json" -d '{"number": 0}' http://127.0.0.1:5000/numbers
	python -m unittest test_numbers.py

infra:
	docker run --name my-postgres \
		-p 5432:5432 \
		--env-file .env \
		-v $(CURDIR)/init.sql:/docker-entrypoint-initdb.d/init.sql \
		postgres:latest