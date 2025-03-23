VERSION  := v0.1.0
GIT_HASH := $(shell git rev-parse --short HEAD)
SERVICE  := ai-teacher
SRC      := $(shell find . -type f -name '*.py' -not -path './.venv/*')
CURR_DIR := $(shell pwd)

.PHONY: help
help: ### Display this help screen.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

.PHONY: lint
lint: ### Improve your code style. (pyflakes, pycodestyle, isort)
	@echo "-> Running import sort..."
	@isort --atomic --multi-line=VERTICAL_HANGING_INDENT ${SRC}
	@echo "-> Running static code analysis..."
	@pyflakes ${SRC}
	@echo "-> Running code style check..."
	@pycodestyle ${SRC} --ignore=E131,E203,E402,E501,W293,W503

.PHONY: local_run
local_run: ### Run the application locally.
	@uvicorn --app-dir=./ --host="0.0.0.0" --port=8000 --workers=1 main:app

.PHONY: local_run_celery_worker
local_run_celery_worker: ### Run the celery worker locally.
	@celery --workdir=./ --app=tasks worker --concurrency=1 --pool=prefork --loglevel=DEBUG

.PHONY: test
test: ### Run the tests. (pytest, pytest-asyncio)
	@(export PYTHONPATH=${PYTHONPATH}:${CURR_DIR} && pytest -v || true)

IMAGE_VERSION := ${VERSION}-${GIT_HASH}

.PHONY: image
image: ### Compile the runtime docker image.
	@(docker build -f ${CURR_DIR}/Dockerfile -t ${SERVICE}-api:${IMAGE_VERSION} .)
