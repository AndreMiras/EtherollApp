VENV_NAME="venv"
ACTIVATE_PATH="$(VENV_NAME)/bin/activate"
PIP=`. $(ACTIVATE_PATH); which pip`
TOX=`which tox`
GARDEN=`. $(ACTIVATE_PATH); which garden`
PYTHON_VERSION="python3.7"
PYTHON="$(VENV_NAME)/bin/python"
SYSTEM_DEPENDENCIES=python3-dev virtualenv build-essential libssl-dev \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
	libffi-dev libgmp3-dev xclip xsel
OS=$(shell lsb_release -si)


all: system_dependencies virtualenv

virtualenv:
	test -d venv || virtualenv -p $(PYTHON_VERSION) venv
	. venv/bin/activate
	$(PIP) install Cython==0.28.6
	# downgrade to setuptools 37, see:
	# https://github.com/ethereum/pyethereum/pull/831
	$(PIP) install setuptools==37.0.0
	$(PIP) install --timeout 120 -r requirements.txt
	$(GARDEN) install qrcode

system_dependencies:
ifeq ($(OS), Ubuntu)
	sudo apt install --yes --no-install-recommends $(SYSTEM_DEPENDENCIES)
endif

clean:
	rm -rf venv/ .tox/ .pytest_cache/

test:
	$(TOX)

uitest: virtualenv
	. $(ACTIVATE_PATH) && \
    $(PYTHON) -m unittest discover --top-level-directory=src/ --start-directory=src/tests/ui/
