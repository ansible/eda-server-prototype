.DEFAULT_GOAL := help

define USAGE_SCRIPT
import sys
import re

for line in sys.stdin:
    if match := re.match(r"^## (.*)$$", line):
            title = match.group(1)
            print(f"\n{title}:\n")
    elif match := re.match(r"([\w/]+):.*?## (.*)$$", line):
        target, help = match.groups()
        print(f"  {target:20s}{help}")
endef
export USAGE_SCRIPT

.PHONY: help
help:  ## Display help.
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo ""
	@python -c "$$USAGE_SCRIPT" < "$(MAKEFILE_LIST)"

## Linters

.PHONY: lint
lint: lint/black lint/isort lint/flake8  ## Run all linters.

.PHONY: lint/black
lint/black:  ## Check code with `black`.
	black --check .

.PHONY: lint/isort
lint/isort:  # Check code with `isort`.
	isort --check .

.PHONY: lint/flake8
lint/flake8:  ## Check code with `flake8`.
	flake8

## Formatting

.PHONY: format
format: format/isort format/black  ## Run all code formatters.

.PHONY: format/isort
format/isort:  ## Format code with `isort`.
	isort .

.PHONY: format/black
format/black:  ## Format code with `black`.
	black .
