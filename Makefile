SHELL := bash
.ONESHELL:


PHONY: install
install: ## Install dependencies
	uv sync


.PHONY: test
test:
	@echo "Running UV sync..."
	uv sync
	@echo "Running Tests..."
	uv run --dev pytest -v --cov-report term-missing --disable-warnings --cov=app tests/


.PHONY: lint
lint:
	@echo "Running Ruff linter..."
	uv run --only-group lint ruff check --fix

.PHONY: bump
bump:
	@echo "🔼 Bumping project version..."
	uv run --only-group version-check python .github/scripts/bump_version.py
	@echo "🔄 Generating new lock file..."
	uv lock
