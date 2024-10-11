# Aiogram template with sqlalchemy, alembic, docker

# Installation

* Fill .env.example and rename to .env
* poetry install
* Run src/main.py

# Migrations

## Create migraion
```shell
alembic revision --autogenerate -m '...'
```

## Apply migration
```shell
alembic upgrade head
```

# Commands

Installation
```shell
poetry install
mv .env.example .env
# Fill in PYTHONPATH and TOKEN in .env
alembic revision --autogenerate -m 'init'
alembic upgrade head
# execute with src/main.py
```
