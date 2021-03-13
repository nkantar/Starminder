.DEFAULT_GOAL := help
.PHONY: help formatcheck lint bandit doccheck typecheck test test-watch covcheck devserve serve sass

help: ## this help dialog
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

formatcheck: ## format with black
	poetry run black --check starminder/

lint: ## lint with flake8
	poetry run flake8 starminder/

bandit: ## check for security issues with bandit
	poetry run bandit -r starminder/ --exclude **/test*.*

doccheck: ## check code docs with pydocstyle
	poetry run pydocstyle starminder/

typecheck: ## check type hints with mypy
	poetry run mypy --strict starminder/**

test: ## run tests with pytest
	STARMINDER_ENVIRONMENT=test poetry run pytest --cov=starminder -vv

test-watch: ## watch tests with pytest-watch
	STARMINDER_ENVIRONMENT=test poetry run pytest-watch -- --cov=starminder -vv

covcheck: ## check code coverage level
	STARMINDER_ENVIRONMENT=test poetry run coverage report --fail-under=0 # TODO 

devserve: ## run dev server
	poetry run python manage.py runserver 0.0.0.0:8000

serve: ## serve with gunicorn
	poetry run gunicorn config.wsgi

sass: ## compile sass
	poetry run pysassc static/style/style.scss static/style/style.css
