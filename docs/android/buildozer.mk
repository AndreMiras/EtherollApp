# Downloads and installs buildozer and its dependencies
# Tested under Ubuntu 18.04 Bionic

all: install_buildozer_system_dependencies install_buildozer

# https://buildozer.readthedocs.io/en/latest/installation.html#android-on-ubuntu-18-04-64bit
install_buildozer_system_dependencies:
	sudo dpkg --add-architecture i386
	sudo apt update -qq > /dev/null
	sudo apt install -qq --yes --no-install-recommends \
	build-essential ccache git libncurses5:i386 libstdc++6:i386 libgtk2.0-0:i386 \
	libpangox-1.0-0:i386 libpangoxft-1.0-0:i386 libidn11:i386 python2.7 \
	python2.7-dev openjdk-8-jdk unzip zlib1g-dev zlib1g:i386

install_buildozer:
	pip install Cython==0.25.2 buildozer
