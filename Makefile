PIP=`. venv/bin/activate; which pip`
TOX=`. venv/bin/activate; which tox`
SYSTEM_DEPENDENCIES="python3-dev"


all: system_dependencies virtualenv

virtualenv:
	test -d venv || virtualenv -p python3 venv
	. venv/bin/activate
	$(PIP) install -r requirements.txt

# Ubuntu 16.04
system_dependencies:
	sudo apt install -y $(SYSTEM_DEPENDENCIES)

test:
	$(TOX)
