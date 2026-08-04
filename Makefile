SHELL := /bin/bash

UV := uv

RUFF = $(UV) run ruff
TY = $(UV) run ty
PYTEST = $(UV) run pytest
SPHINX = $(UV) run --with-requirements $(DOCS)/requirements.txt sphinx-build
VERSION = $(shell $(UV) version --short)

SRC = prettyconf
TEST = tests
DOCS = docs
CI_WORKFLOW = .github/workflows/tests.yml

# The supported interpreters are declared once, in the package classifiers.
PYTHON_VERSIONS = $(shell sed -n 's/.*Programming Language :: Python :: \(3\.[0-9][0-9]*\)".*/\1/p' pyproject.toml)

# Run any target against another interpreter with `make test PYTHON=3.10`. Each
# version gets its own virtualenv, so switching back and forth does not rebuild
# the default environment. The setup stamp lives inside the virtualenv on
# purpose: removing the virtualenv has to invalidate it, or the next run would
# silently reuse an environment that was never synced.
VENV = $(if $(PYTHON),.venv$(subst .,,$(PYTHON)),.venv)
SETUP = $(VENV)/.make-setup
export UV_PROJECT_ENVIRONMENT := $(VENV)
ifdef PYTHON
export UV_PYTHON := $(PYTHON)
endif

.DEFAULT_GOAL := help

# Targets
.make/ensure-uv:
	@$(UV) --version > /dev/null 2>&1 || ./bin/install-uv.sh
	@mkdir -p .make/ && touch .make/ensure-uv

uv.lock: .make/ensure-uv pyproject.toml
	$(UV) lock --no-upgrade
	touch uv.lock  # force update even when not changed

$(SETUP): uv.lock
	$(UV) sync --locked --all-extras
	@touch $(SETUP)

# Development
.PHONY: setup
setup: $(SETUP) ## install all requirements and prepare the environment for local development

.PHONY: update-deps
update-deps: $(SETUP) ## update all dependencies to their latest versions
	$(UV) lock -U
	$(UV) sync -U --all-extras

.PHONY: fix-lock
fix-lock: .make/ensure-uv ## regenerate and stage the uv lock file
	$(UV) lock
	@git add uv.lock

.PHONY: lint
lint: $(SETUP) check-versions ## run linters on all files
	$(RUFF) check $(SRC) $(TEST)
	$(RUFF) format --check $(SRC) $(TEST)

.PHONY: format
format: $(SETUP) ## run formatters on all files
	$(RUFF) format $(SRC) $(TEST)
	$(RUFF) check $(SRC) $(TEST) --fix

.PHONY: typecheck
typecheck: $(SETUP) ## run type checking with ty
	$(TY) check $(SRC) $(TEST)/typing_examples.py

.PHONY: test
test: $(SETUP) ## run all tests (use ARGS="..." to pass extra arguments to pytest)
	$(PYTEST) -v $(TEST) $(ARGS)

.PHONY: test-all
test-all: ## run the test suite against every supported python version
	@for version in $(PYTHON_VERSIONS); do \
		echo "--- python $$version ---"; \
		$(MAKE) --no-print-directory test PYTHON=$$version ARGS="$(ARGS)" || exit 1; \
	done

.PHONY: check-versions
check-versions: ## fail when the CI matrix drifts from the supported python classifiers
	@declared=$$(echo $(PYTHON_VERSIONS) | xargs); \
	matrix=$$(sed -n 's/^ *python-version: *\[\(.*\)\] *$$/\1/p' $(CI_WORKFLOW) | tr -d '"' | tr ',' ' ' | xargs); \
	if [ "$$declared" != "$$matrix" ]; then \
		echo "$(CI_WORKFLOW) tests [$$matrix], but pyproject.toml declares support for [$$declared]"; \
		exit 1; \
	fi

.PHONY: coverage
coverage: $(SETUP) ## run all tests with coverage report
	$(PYTEST) -v --cov=$(SRC) --cov-report=term --cov-report=xml --cov-report=term-missing $(TEST) $(ARGS)

.PHONY: docs
docs: $(SETUP) ## build the HTML documentation into docs/build/html
	$(SPHINX) -b html $(DOCS)/source $(DOCS)/build/html

.PHONY: build
build: $(SETUP) ## build the sdist and the wheel into dist/
	rm -rf dist
	$(UV) build

.PHONY: release
release: lint test build ## tag the current version and publish the GitHub release (CI uploads to PyPI)
	git tag -a "$(VERSION)" -m "Release $(VERSION)"
	git push origin "$(VERSION)"
	gh release create "$(VERSION)" --title "$(VERSION)" --generate-notes

.PHONY: clean
clean: ## remove all makefile targets and build artifacts
	rm -f .make/[a-z]* .venv*/.make-setup
	rm -rf dist build coverage.xml .coverage .ruff_cache .pytest_cache $(DOCS)/build
	# a stale egg-info shadows the installed metadata and reports the wrong version
	rm -rf $(SRC).egg-info
	-find . -name "__pycache__" -type d -prune -exec rm -rf {} +
	-find . -name "*.py[co]" -delete

.PHONY: help
help: ## show this help text
	@grep -h -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-14s\033[0m %s\n", $$1, $$2}'
