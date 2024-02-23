ifneq (,$(wildcard ./.env))
    include .env
    export
    DOCKER_ENV_FILE_PARAM = --env-file .env
endif

VENV_NAME?=.venv
PYTHON_VERSION?=3.9
PYTHON=${VENV_NAME}/bin/python

venv: $(VENV_NAME)/bin/activate

ifeq (, $(shell which python$(PYTHON_VERSION)))
	$(error "No python$(PYTHON_VERSION) in $(PATH)")
endif

.PHONY: lint
lint: venv ## lint source code
	@echo "Linting src ... 🧹"
	@$(VENV_NAME)/bin/ruff check

.PHONY: clean
clean: ## clean project directory
	rm -rf .tox .ruff_cache .venv __pycache__

.PHONY: tests
tests: venv ## run tests
	@echo "Running tests ... 🧪"
	@$(VENV_NAME)/bin/python -m tox

$(VENV_NAME)/bin/activate: requirements.txt
	test -d $(VENV_NAME) || python$(PYTHON_VERSION) -m venv $(VENV_NAME)
	${PYTHON} -m pip install -U pip
	${PYTHON} -m pip install -r requirements.txt
	# ensure venv is rebuild when requirements.txt changes
	touch $(VENV_NAME)/bin/activate
