# Docker image for running building the APK via buildozer
# Build with:
# docker build --tag=buildozer .
# Run with:
# docker run buildozer /bin/sh -c 'buildozer android debug'
# Or for interactive shell:
# docker run -it --rm buildozer
FROM ubuntu:18.04

ENV USER="user"
ENV HOME_DIR="/home/${USER}"
ENV WORK_DIR="${HOME_DIR}" \
    PATH="${HOME_DIR}/.local/bin:${PATH}"


# configure locale
RUN apt update -qq > /dev/null && apt install --yes --no-install-recommends \
    locales && \
    locale-gen en_US.UTF-8
ENV LANG="en_US.UTF-8" \
    LANGUAGE="en_US.UTF-8" \
    LC_ALL="en_US.UTF-8"

# install system dependencies (required to setup all the tools)
RUN apt update -qq > /dev/null && apt install --yes --no-install-recommends \
    make curl ca-certificates xz-utils unzip openjdk-8-jdk sudo python-pip \
    python-setuptools

# install build dependencies (required to successfully build the project)
# TODO


# prepare non root env
RUN useradd --create-home --shell /bin/bash ${USER}
# with sudo access and no password
RUN usermod -append --groups sudo ${USER}
RUN echo "%sudo ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

USER ${USER}

WORKDIR ${WORK_DIR}
COPY . ${WORK_DIR}

# downloads and installs CrystaX NDK
RUN make -f docs/android/crystax_ndk.mk

# downloads and installs Android SDK
RUN make -f docs/android/android_sdk.mk

# install buildozer and dependencies
RUN make -f docs/android/buildozer.mk
