# Docker image for installing dependencies on Linux and running tests.
# Build with:
# docker build --tag=etheroll .
# Run with:
# docker run etheroll /bin/sh -c '. venv/bin/activate && make test'
# Or for interactive shell:
# docker run -it --rm etheroll
# TODO:
#	- delete archives to keep small the container small
#	- setup caching (for apt, and pip)
FROM ubuntu:16.04

# configure locale
RUN apt update -qq > /dev/null && apt install --yes --no-install-recommends \
    locales && \
    locale-gen en_US.UTF-8
ENV LANG="en_US.UTF-8" \
    LANGUAGE="en_US.UTF-8" \
    LC_ALL="en_US.UTF-8"

# install system dependencies
RUN apt update -qq > /dev/null && apt install --yes --no-install-recommends \
	python3 python3-dev virtualenv make lsb-release pkg-config git build-essential \
    libssl-dev tox

# install kivy system dependencies
# https://kivy.org/docs/installation/installation-linux.html#dependencies-with-sdl2
RUN apt install --yes --no-install-recommends \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev

WORKDIR /app
COPY . /app
RUN make virtualenv
