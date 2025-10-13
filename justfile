sync:
    uv sync

syncprod:
    uv sync --no-dev

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

schedulejobs:
    uv run python manage.py setup_schedules

collectstatic:
    uv run python manage.py collectstatic --noinput

devserve:
    uv run python manage.py runserver --nostatic

prodserve:
    uv run granian starminder.wsgi:application --host 0.0.0.0 --port 8000 --interface wsgi --no-ws --workers 2 --runtime-threads 1 --blocking-threads 4 --backpressure 8 --log-level debug --log --process-name granian[starminder]

worker:
    uv run python manage.py qcluster

djangocheck:
    uv run python manage.py check

deploy:
    bash scripts/deploy.sh

startjobs:
    uv run python manage.py start_jobs
