.PHONY: all clean tests

SHELL := /bin/bash

GIT_COMMIT := $(shell git rev-parse HEAD)
GIT_SHORT := $(shell git rev-parse --short HEAD)

clean:
	@echo "Cleaning up..."
	rm -rf build dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type f -name '*.pyd' -delete
	find . -type f -name '*.so' -delete
	find . -type f -name '*.dll' -delete
	find . -type f -name '*.dylib' -delete

export PYTHONPATH := $(shell pwd)

format:
	@echo "Formatting code..."
	ruff check --fix .
	isort .
	black .
