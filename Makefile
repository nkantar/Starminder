.DEFAULT_GOAL := help
.PHONY: help run test watch check-format check-typehints check-lint check-docs

help: ## this help dialog
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

run: ## run Starminder
	poetry run python starminder.py

test: ## run tests
	poetry run pytest

watch: ## watch tests
	poetry run pytest-watch

check-format: ## check code formatting with Black
	poetry run black --check .

check-typehints: ## check type hints with mypy
	poetry run mypy --strict starminder.py constants.py

check-lint: ## checking for linter errors with flake8
	poetry run flake8 .

check-docs: ## check docstyle with pydocstyle
	poetry run pydocstyle starminder.py constants.py
