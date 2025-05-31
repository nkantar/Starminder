# NOTE Some of the commands assume uv is present.


# ==============================================================================
# general

# run dev modd config
dev:
    modd

# run PostgreSQL via Docker compose
docker-compose:
    docker compose up

# run Django dev server
serve:
    uv run python manage.py runserver


# ==============================================================================
# code quality

# check formatting via ruff
formatcheck:
    uv run ruff format --check .

# check type hints via mypy
typecheck:
    uv run mypy .

# run linter via ruff
lint:
    uv run ruff check .

# run tests via pytest and coverage
test:
    uv run pytest

# run all checks
checkall:
    just formatcheck
    just typecheck
    just lint
    just test
