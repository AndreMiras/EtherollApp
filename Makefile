VENV_NAME="venv"
ACTIVATE_PATH="$(VENV_NAME)/bin/activate"
PIP=`. $(ACTIVATE_PATH); which pip`
TOX=`which tox`
GARDEN=`. $(ACTIVATE_PATH); which garden`
PYTHON_VERSION="python3.7"
PYTHON=$(VENV_NAME)/bin/python
ISORT=$(VENV_NAME)/bin/isort
FLAKE8=$(VENV_NAME)/bin/flake8
TWINE=`which twine`
SOURCES=src/ setup.py
SYSTEM_DEPENDENCIES=python3-dev virtualenv build-essential libssl-dev \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
	libffi-dev libgmp3-dev xclip xsel
OS=$(shell lsb_release -si)


all: system_dependencies virtualenv

virtualenv:
	test -d venv || virtualenv -p $(PYTHON_VERSION) venv
	. venv/bin/activate
	$(PIP) install Cython==0.28.6
	$(PIP) install --timeout 120 -r requirements.txt

system_dependencies:
ifeq ($(OS), Ubuntu)
	sudo apt install --yes --no-install-recommends $(SYSTEM_DEPENDENCIES)
endif

run:
	$(PYTHON) src/main.py

test:
	$(TOX)

lint/isort-check: virtualenv
	$(ISORT) --check-only --recursive --diff $(SOURCES)

lint/isort-fix: virtualenv
	$(ISORT) --recursive $(SOURCES)

lint/flake8: virtualenv
	$(FLAKE8) $(SOURCES)

lint: lint/isort-check lint/flake8

release/clean:
	rm -rf dist/ build/

release/build: release/clean clean
	$(PYTHON) setup.py sdist bdist_wheel
	$(TWINE) check dist/*

release/upload:
	$(TWINE) upload dist/*

clean:
	py3clean src/
	rm -rf .pytest_cache/
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name "*.egg-info" -exec rm -r {} +

clean/venv: clean
	rm -rf $(VENV_NAME) .tox/

uitest: virtualenv
	. $(ACTIVATE_PATH) && \
    $(PYTHON) -m unittest discover --top-level-directory=src/ --start-directory=src/etherollapp/tests/ui/
