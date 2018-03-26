PIP=`. venv/bin/activate; which pip`
TOX=`. venv/bin/activate; which tox`
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
