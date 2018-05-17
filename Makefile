VENV_NAME="venv"
ACTIVATE_PATH="$(VENV_NAME)/bin/activate"
PIP=`. $(ACTIVATE_PATH); which pip`
TOX=`. $(ACTIVATE_PATH); which tox`
GARDEN=`. $(ACTIVATE_PATH); which garden`
PYTHON="$(VENV_NAME)/bin/python"
SYSTEM_DEPENDENCIES=python3-dev virtualenv build-essential libssl-dev \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
OS=$(shell lsb_release -si)


all: system_dependencies virtualenv

virtualenv:
	test -d venv || virtualenv -p python3 venv
	. venv/bin/activate
	$(PIP) install Cython==0.26.1
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
	rm -rf venv/ .tox/

test:
	$(TOX)

uitest: virtualenv
	. $(ACTIVATE_PATH) && \
    $(PYTHON) -m unittest discover --top-level-directory=src/ --start-directory=src/tests/ui/
