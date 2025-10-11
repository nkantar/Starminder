format:
    uv run ruff format .

formatcheck:
    uv run ruff format --check .

lint:
    uv run ruff check .

lintfix:
    uv run ruff check . --fix

typecheck:
    uv run ty check .

test:
    uv run pytest

makemigrations:
    uv run python manage.py makemigrations

migrate:
    uv run python manage.py migrate

devserve:
    uv run python manage.py runserver

worker:
    uv run python manage.py qcluster

djangocheck:
    uv run python manage.py check
