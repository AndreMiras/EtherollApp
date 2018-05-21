# Docker image for running F-Droid build scripts.
# Build with:
# docker build --tag=fdroid .
# Run with:
# docker run fdroid /bin/sh -c 'fdroid build -v -l com.github.andremiras.etheroll'
# Or for interactive shell:
# docker run -it --rm fdroid
FROM ubuntu:18.04

ENV WORK_DIR="/app" \
    FDROIDDATA_ARCHIVE="fdroiddata-master.tar.bz2"
ENV FDROIDDATA_DL_URL="https://gitlab.com/fdroid/fdroiddata/-/archive/master/${FDROIDDATA_ARCHIVE}"

# configure locale
RUN apt update -qq > /dev/null && apt install --yes --no-install-recommends \
    locales && \
    locale-gen en_US.UTF-8
ENV LANG="en_US.UTF-8" \
    LANGUAGE="en_US.UTF-8" \
    LC_ALL="en_US.UTF-8"

# install system dependencies
RUN apt update -qq > /dev/null && apt install --yes --no-install-recommends \
    python3 python3-pip python3-distutils python3-setuptools git curl wget

# make python3 the default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1 && \
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

# install fdroidserver and fdroiddata
RUN pip install fdroidserver
RUN curl --location --progress-bar "${FDROIDDATA_DL_URL}" --output "${FDROIDDATA_ARCHIVE}" && \
    mkdir "${WORK_DIR}" && \
    tar -xf "${FDROIDDATA_ARCHIVE}" --directory "${WORK_DIR}"

WORKDIR ${WORK_DIR}
