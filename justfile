############################################################
# All commands are to be run inside a virtual environment. #
# E.g.,                                                    #
#     uv run just serve                                    #
############################################################


# run dev modd config
dev:
    modd

# run PostgreSQL via Docker compose
docker-compose:
    docker compose up

# run Django dev server
serve:
    python manage.py runserver
