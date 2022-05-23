up:
	docker-compose up

black:
	docker-compose run --rm app black .

flake8:
	docker-compose run --rm app flake8 .

test:
	docker-compose run --rm app pytest $(extra)

isort:
	docker-compose run --rm app isort app/
