VIRTUAL_ENV ?= venv
ACTIVATE_PATH=$(VIRTUAL_ENV)/bin/activate
PIP=$(VIRTUAL_ENV)/bin/pip
TOX=`which tox`
PYTHON_VERSION=python3.7
PYTHON=$(VIRTUAL_ENV)/bin/python
ISORT=$(VIRTUAL_ENV)/bin/isort
FLAKE8=$(VIRTUAL_ENV)/bin/flake8
TWINE=`which twine`
SOURCES=src/ setup.py
SYSTEM_DEPENDENCIES= \
	build-essential \
	git \
	libffi-dev \
	libgmp3-dev \
	libsdl2-dev \
	libsdl2-image-dev \
	libsdl2-mixer-dev \
	libsdl2-ttf-dev \
	libssl-dev \
	pkg-config \
	python3.7 \
	python3.7-dev \
	tox \
	virtualenv \
	xclip \
	xsel
OS=$(shell lsb_release -si 2>/dev/null || uname)
ifndef CI
DEVICE=--device=/dev/video0:/dev/video0
endif


all: system_dependencies virtualenv

$(VIRTUAL_ENV):
	virtualenv --python $(PYTHON_VERSION) $(VIRTUAL_ENV)
	$(PIP) install Cython==0.28.6
	$(PIP) install --timeout 120 --requirement requirements.txt

virtualenv: $(VIRTUAL_ENV)

system_dependencies:
ifeq ($(OS), Ubuntu)
	sudo apt install --yes --no-install-recommends $(SYSTEM_DEPENDENCIES)
endif

run: virtualenv
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
	rm -rf $(VIRTUAL_ENV) .tox/

uitest: virtualenv
	$(PYTHON) -m unittest discover --top-level-directory=src/ --start-directory=src/etherollapp/tests/ui/

docker/pull/linux:
	docker pull andremiras/etherollapp-linux

docker/build/linux:
	docker build --tag=andremiras/etherollapp-linux --file=dockerfiles/Dockerfile-linux .

docker/run/test:
	docker run --env-file dockerfiles/env.list -v /tmp/.X11-unix:/tmp/.X11-unix $(DEVICE) etherollapp-linux 'make test'

docker/run/app:
	docker run --env-file dockerfiles/env.list -v /tmp/.X11-unix:/tmp/.X11-unix $(DEVICE) etherollapp-linux 'make run'

docker/run/shell:
	docker run --env-file dockerfiles/env.list -v /tmp/.X11-unix:/tmp/.X11-unix $(DEVICE) -it --rm etherollapp-linux
