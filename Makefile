.DEFAULT_GOAL := help
.PHONY: help run test watch

help: ## this help dialog
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

run: ## run Starminder
	poetry run python starminder.py

test: ## run tests
	poetry run pytest

watch: ## watch tests
	poetry run pytest-watch
