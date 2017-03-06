metadb
======

## Installation

### Docker

Setup:

Build the docker containers:

    docker-compose build

Start all containers:

    docker-compose up

Once the containers are up, you can initialise the database:

    docker-compose run --rm web python manage.py init_db
    docker-compose run --rm web python manage.py fixtures

To make a web token to submit/retrieve using the webservice

    docker-compose run --rm web python manage.py addtoken --admin