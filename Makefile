VIRTUAL_ENV ?= venv
ACTIVATE_PATH=$(VIRTUAL_ENV)/bin/activate
PIP=$(VIRTUAL_ENV)/bin/pip
TOX=`which tox`
PYTHON_MAJOR_VERSION=3
PYTHON_MINOR_VERSION=7
PYTHON_VERSION=$(PYTHON_MAJOR_VERSION).$(PYTHON_MINOR_VERSION)
PYTHON_MAJOR_MINOR=$(PYTHON_MAJOR_VERSION)$(PYTHON_MINOR_VERSION)
PYTHON_WITH_VERSION=python$(PYTHON_VERSION)
PYTHON=$(VIRTUAL_ENV)/bin/python
ISORT=$(VIRTUAL_ENV)/bin/isort
FLAKE8=$(VIRTUAL_ENV)/bin/flake8
PYTEST=$(VIRTUAL_ENV)/bin/pytest
TWINE=`which twine`
SOURCES=src/ setup.py
SYSTEM_DEPENDENCIES_LINUX= \
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
	python$(PYTHON_VERSION) \
	python$(PYTHON_VERSION)-dev \
	tox \
	virtualenv \
	xclip \
	xsel
SYSTEM_DEPENDENCIES_ANDROID= \
    autoconf \
    automake \
    bsdtar \
    ca-certificates \
    curl \
    libffi-dev \
    libltdl-dev \
    libpython$(PYTHON_VERSION)-dev \
    libtool \
    openjdk-8-jdk \
    python2.7 \
    python$(PYTHON_VERSION) \
    python3-pip \
    python3-setuptools \
    sudo \
    unzip \
    xz-utils \
    zip
OS=$(shell lsb_release -si 2>/dev/null || uname)
ifndef CI
DEVICE=--device=/dev/video0:/dev/video0
endif

system_dependencies_linux:
ifeq ($(OS), Ubuntu)
	sudo apt install --yes --no-install-recommends $(SYSTEM_DEPENDENCIES_LINUX)
endif
system_dependencies_android:
ifeq ($(OS), Ubuntu)
	sudo apt install --yes --no-install-recommends $(SYSTEM_DEPENDENCIES_ANDROID)
endif


all: virtualenv

$(VIRTUAL_ENV):
	virtualenv --python $(PYTHON_WITH_VERSION) $(VIRTUAL_ENV)
	$(PIP) install Cython==0.28.6
	$(PIP) install --timeout 120 --requirement requirements.txt

virtualenv: $(VIRTUAL_ENV)

run: virtualenv
	$(PYTHON) src/main.py

test: virtualenv
	PYTHONPATH=src $(PYTEST) --ignore src/etherollapp/tests/ui/ src/etherollapp/tests/

uitest: virtualenv
	$(PYTHON) -m unittest discover --top-level-directory=src/ --start-directory=src/etherollapp/tests/ui/

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

buildozer/android/debug:
	@if test -n "$$CI"; then sed 's/log_level = [0-9]/log_level = 1/' -i buildozer.spec; fi; \
	buildozer android debug

docker/pull/linux:
	docker pull andremiras/etherollapp-linux:latest

docker/pull/android:
	docker pull andremiras/etherollapp-android:latest

docker/build/linux:
	docker build --cache-from=andremiras/etherollapp-linux --tag=andremiras/etherollapp-linux --file=dockerfiles/Dockerfile-linux .

docker/build/android:
	docker build --cache-from=andremiras/etherollapp-linux --tag=andremiras/etherollapp-android --file=dockerfiles/Dockerfile-android .

docker/run/test/linux:
	docker run --env-file dockerfiles/env.list -v /tmp/.X11-unix:/tmp/.X11-unix $(DEVICE) andremiras/etherollapp-linux 'make test'

docker/run/test/android:
	docker run --env-file dockerfiles/env.list andremiras/etherollapp-android 'make buildozer/android/debug'

docker/run/app:
	docker run --env-file dockerfiles/env.list -v /tmp/.X11-unix:/tmp/.X11-unix $(DEVICE) andremiras/etherollapp-linux 'make run'

docker/run/shell/linux:
	docker run --env-file dockerfiles/env.list -v /tmp/.X11-unix:/tmp/.X11-unix $(DEVICE) -it --rm andremiras/etherollapp-linux

docker/run/shell/android:
	docker run --env-file dockerfiles/env.list -v /tmp/.X11-unix:/tmp/.X11-unix $(DEVICE) -it --rm andremiras/etherollapp-android
