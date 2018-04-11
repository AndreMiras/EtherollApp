VENV_NAME="venv"
ACTIVATE_PATH="$(VENV_NAME)/bin/activate"
PIP=`. $(ACTIVATE_PATH); which pip`
TOX=`. $(ACTIVATE_PATH); which tox`
PYTHON="$(VENV_NAME)/bin/python"
SYSTEM_DEPENDENCIES="python3-dev"
OS=$(shell lsb_release -si)


all: system_dependencies virtualenv

virtualenv:
	test -d venv || virtualenv -p python3 venv
	. venv/bin/activate
	$(PIP) install Cython==0.26
	# downgrade to setuptools 37, see:
	# https://github.com/ethereum/pyethereum/pull/831
	$(PIP) install setuptools==37.0.0
	$(PIP) install -r requirements.txt

system_dependencies:
ifeq ($(OS), Ubuntu)
	sudo apt install -y $(SYSTEM_DEPENDENCIES)
endif

clean:
	rm -rf venv/ .tox/

test: virtualenv
	$(TOX)

uitest: virtualenv
	. $(ACTIVATE_PATH) && \
    $(PYTHON) -m unittest discover --start-directory=src/tests/ui/
