.DEFAULT_GOAL := help

# Override PYTHON when creating an environment with a pyenv interpreter.
PYTHON ?= python3.7
VENV ?= .venv37
VENV_PYTHON := $(VENV)/bin/python
ARGS ?=
CONFIG ?= config.json
TEST_ARGS ?=
DOCS_PORT ?= 8000
SERVER_PORT ?= 9000

.PHONY: help venv install check-env check test test-integration run server sender docs show-docs clean clean-venv

help: ## List available targets (default).
	@awk 'BEGIN { FS = ":.*## " } /^[a-z-]+:.*## / { printf "  %-20s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@printf '\nOverrides: PYTHON, VENV, CONFIG, ARGS, TEST_ARGS, DOCS_PORT, SERVER_PORT\n'

venv: ## Create the Python 3.7 environment if it does not exist.
	@if [ ! -x "$(VENV_PYTHON)" ]; then "$(PYTHON)" -m venv "$(VENV)"; fi
	@"$(VENV_PYTHON)" -c 'import sys; assert sys.version_info[:2] == (3, 7), "This project requires a Python 3.7 environment"'

install: venv ## Install runtime, test, and documentation dependencies.
	"$(VENV_PYTHON)" -m pip install -r requirements-dev.txt -r requirements-docs.txt
	"$(VENV_PYTHON)" -m pip check

check-env:
	@test -x "$(VENV_PYTHON)" || { printf 'Missing environment. Run make install (override PYTHON if needed).\n'; exit 1; }

check: check-env ## Check Python version and installed dependency consistency.
	"$(VENV_PYTHON)" --version
	"$(VENV_PYTHON)" -m pip check

test: check-env ## Run unit tests without hardware or a WebSocket server.
	"$(VENV_PYTHON)" -m pytest --ignore=tests/test_integration.py -v $(TEST_ARGS)

test-integration: check-env ## Run the smoke test; first start make server on port 9000.
	"$(VENV_PYTHON)" -m pytest tests/test_integration.py -v $(TEST_ARGS)

run: check-env ## Run the exporter using CONFIG=config.json.
	PYTHONPATH=src "$(VENV_PYTHON)" app/exporter-ecoadapt.py --config "$(CONFIG)" $(ARGS)

server: check-env ## Run the development WebSocket receiver (SERVER_PORT=9000).
	"$(VENV_PYTHON)" dev/server.py --port "$(SERVER_PORT)"

sender: check-env ## Send a sample reading; requires the receiver on port 9000.
	PYTHONPATH=src "$(VENV_PYTHON)" dev/test_sender.py

docs: check-env ## Rebuild all Sphinx HTML documentation; fail on warnings.
	"$(VENV_PYTHON)" -m sphinx -E -a -W --keep-going -b html docs docs/_build/html

show-docs: docs ## Build and serve documentation at localhost (DOCS_PORT=8000).
	@printf 'Open http://localhost:%s (Ctrl+C to stop).\n' "$(DOCS_PORT)"
	"$(VENV_PYTHON)" -m http.server "$(DOCS_PORT)" --bind 127.0.0.1 --directory docs/_build/html

clean: ## Remove generated docs and project caches; keep virtual environments.
	rm -rf docs/_build .pytest_cache
	find src app dev tests docs -type d -name __pycache__ -prune -exec rm -rf {} +
	find src app dev tests docs -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete

clean-venv: ## Remove the virtual environment and its packages; recreate with make install.
	@if [ ! -e "$(VENV)" ] && [ ! -L "$(VENV)" ]; then \
		printf 'Virtual environment already absent.\n'; \
	elif [ -L "$(VENV)" ] || [ ! -f "$(VENV)/pyvenv.cfg" ]; then \
		printf 'Refusing to remove a symlink or directory without pyvenv.cfg.\n'; exit 1; \
	else \
		rm -rf -- "$(VENV)"; \
	fi
