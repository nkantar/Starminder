############################################################
# All commands are to be run inside a virtual environment. #
# E.g.,                                                    #
#     uv run just serve                                    #
############################################################


#########
# general

# run dev modd config
dev:
    modd

# run PostgreSQL via Docker compose
docker-compose:
    docker compose up

# run Django dev server
serve:
    python manage.py runserver


##############
# code quality

# check formatting via ruff
formatcheck:
    ruff format --check .

# check type hints via mypy
typecheck:
    mypy .

# run linter via ruff
lint:
    ruff check .

# run tests via pytest and coverage
test:
    pytest

# run all checks
checkall:
    just formatcheck
    just typecheck
    just lint
    just test
