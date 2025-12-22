SHELL := bash
.ONESHELL:

.PHONY: test
test:
	@echo "Running UV sync..."
	uv sync
	@echo "Running Tests..."
	uv run --dev pytest -v --cov-report term-missing --disable-warnings --cov=app tests/