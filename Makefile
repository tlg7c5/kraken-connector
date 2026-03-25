#* Variables
SHELL := /usr/bin/env bash
PYTHON := python
PYTHONPATH := `pwd`

#* Docker variables
IMAGE := kraken-connector
VERSION := latest

.PHONY: install
install: ## Install the pdm environment and install the pre-commit hooks
	@echo "🚀 Creating virtual environment using pyenv and pdm"
	@pdm install
	@pdm run pre-commit install

.PHONY: generate
generate: ## Regenerate API client code from openapi.json
	@echo "🚀 Regenerating client from OpenAPI spec"
	@pdm run openapi-python-client update --path openapi.json

.PHONY: check
check: ## Run code quality tools.
	@echo "🚀 Checking PDM lock file consistency with 'pyproject.toml': Running pdm lock --check"
	@pdm lock --check
	@echo "🚀 Linting code: Running pre-commit"
	@pdm run pre-commit run -a
	@echo "🚀 Static type checking: Running mypy"
	@pdm run mypy
	@echo "🚀 Checking for obsolete dependencies: Running deptry"
	@pdm run deptry .

.PHONY: test
test: ## Test the code with pytest
	@echo "🚀 Testing code: Running pytest"
	@pdm run pytest --cov --cov-config=pyproject.toml --cov-report=xml

#* Docker
# Example: make docker-build VERSION=latest
# Example: make docker-build IMAGE=some_name VERSION=0.1.0
.PHONY: docker-build
docker-build:
	@echo Building docker $(IMAGE):$(VERSION) .
	docker buildx build --platform linux/arm64 \
		-t $(IMAGE):$(VERSION) . \
		-f ./docker/Dockerfile --no-cache

# Example: make docker-remove VERSION=latest
# Example: make docker-remove IMAGE=some_name VERSION=0.1.0
.PHONY: docker-remove
docker-remove:
	@echo Removing docker $(IMAGE):$(VERSION) .
	docker rmi -f $(IMAGE):$(VERSION)

.PHONY: local-build
local-build:
	@echo Building docker $(IMAGE):$(VERSION) .
	docker buildx build --platform linux/arm64 \
		-t $(IMAGE):$(VERSION) . \
		-f ./docker/dev/Dockerfile

.PHONY: local
local:
	@echo Creating local dev environment
	docker run --name $(IMAGE) -v /var/run/docker.sock:/var/run/docker.sock -v $(PYTHONPATH):/app -it --rm $(IMAGE) bash

.PHONY: build
build: clean-build ## Build wheel file using pdm
	@echo "🚀 Creating wheel file"
	@pdm build

.PHONY: clean-build
clean-build: ## clean build artifacts
	@rm -rf dist

.PHONY: publish
publish: ## publish a release to pypi.
	@echo "🚀 Publishing."
	@pdm publish --no-build -u __token__ -P $(PYPI_TOKEN)

.PHONY: build-and-publish
build-and-publish: build publish ## Build and publish.

.PHONY: docs-test
docs-test: ## Test if documentation can be built without warnings or errors
	@pdm run mkdocs build -s

.PHONY: docs
docs: ## Build and serve the documentation
	@pdm run mkdocs serve

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
