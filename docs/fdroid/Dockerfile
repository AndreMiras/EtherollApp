# Docker image for running F-Droid build scripts.
# Build with:
# docker build --tag=fdroid .
# Run with:
# docker run fdroid /bin/sh -c 'fdroid build -v -l com.github.andremiras.etheroll'
# Or for interactive shell:
# docker run -it --rm fdroid
FROM ubuntu:18.04

# configure locale
RUN apt update -qq > /dev/null && apt install --yes --no-install-recommends \
    locales && \
    locale-gen en_US.UTF-8
ENV LANG="en_US.UTF-8" \
    LANGUAGE="en_US.UTF-8" \
    LC_ALL="en_US.UTF-8"

# install system dependencies
RUN apt update -qq > /dev/null && apt install --yes --no-install-recommends \
	python3 python3-dev

WORKDIR /app
