PIP=`. venv/bin/activate; which pip`
TOX=`. venv/bin/activate; which tox`
SYSTEM_DEPENDENCIES="python3-dev"
OS=$(shell lsb_release -si)


all: system_dependencies virtualenv

virtualenv:
	test -d venv || virtualenv -p python3 venv
	. venv/bin/activate
	$(PIP) install -r requirements.txt

system_dependencies:
ifeq ($(OS), Ubuntu)
	sudo apt install -y $(SYSTEM_DEPENDENCIES)
endif

clean:
	rm -rf venv

test: virtualenv
	$(TOX)
