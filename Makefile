ifneq (,$(wildcard ./.env))
    include .env
    export
    DOCKER_ENV_FILE_PARAM = --env-file .env
endif

VENV_NAME?=.venv
PYTHON_VERSION?=3.9
PYTHON=${VENV_NAME}/bin/python

venv: $(VENV_NAME)/bin/activate

$(VENV_NAME)/bin/activate: requirements.txt
	test -d $(VENV_NAME) || python -m virtualenv -p $(PYTHON_VERSION) $(VENV_NAME)
	${PYTHON} -m pip install -U pip
	${PYTHON} -m pip install -r requirements.txt
	# ensure venv is rebuild when requirements.txt changes
	touch $(VENV_NAME)/bin/activate
