format:
    uv run ruff format .

lint:
    uv run ruff check .

typecheck:
    uv run ty check .

makemigrations:
    uv run python manage.py makemigrations

migrate:
    uv run python manage.py migrate

devserve:
    uv run python manage.py runserver
