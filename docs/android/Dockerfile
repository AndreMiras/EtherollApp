# Docker image for building Android APKs via buildozer
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
ENV DOCKERFILES_VERSION="master" \
    DOCKERFILES_URL="https://raw.githubusercontent.com/AndreMiras/dockerfiles"
ENV MAKEFILES_URL="${DOCKERFILES_URL}/${DOCKERFILES_VERSION}/buildozer_android_new"
# currently needed because buildozer still uses `tools/android` binary
# even though we have the new `tools/bin/sdkmanager` available
ENV USE_SDK_WRAPPER=true


# configure locale
RUN apt update -qq > /dev/null && apt install -qq --yes --no-install-recommends \
    locales && \
    locale-gen en_US.UTF-8
ENV LANG="en_US.UTF-8" \
    LANGUAGE="en_US.UTF-8" \
    LC_ALL="en_US.UTF-8"

# install system dependencies (required to setup all the tools)
RUN apt update -qq > /dev/null && apt install -qq --yes --no-install-recommends \
    make curl ca-certificates xz-utils unzip openjdk-8-jdk sudo python-pip \
    python-setuptools

# install build dependencies (required to successfully build the project)
# TODO: should this go to a Makefile instead?
RUN apt install -qq --yes --no-install-recommends \
    python3.6 libpython3.6-dev python3-setuptools \
    autoconf automake libtool libltdl-dev libffi-dev

# prepare non root env
RUN useradd --create-home --shell /bin/bash ${USER}
# with sudo access and no password
RUN usermod -append --groups sudo ${USER}
RUN echo "%sudo ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

USER ${USER}
WORKDIR ${WORK_DIR}

# downloads and installs CrystaX NDK
RUN curl --location --progress-bar ${MAKEFILES_URL}/crystax_ndk.mk --output crystax_ndk.mk
RUN make -f crystax_ndk.mk

# downloads and installs Android SDK
RUN curl --location --progress-bar ${MAKEFILES_URL}/android_sdk.mk --output android_sdk.mk
RUN make -f android_sdk.mk

# install buildozer and dependencies
RUN curl --location --progress-bar ${MAKEFILES_URL}/buildozer.mk --output buildozer.mk
RUN make -f buildozer.mk

# links SDK and NDK to where buildozer is expecting to see them
RUN mkdir -p ${HOME}/.buildozer/android/platform
RUN ln -sfn ${HOME}/.android/android-sdk ${HOME}/.buildozer/android/platform/android-sdk-20
RUN ln -sfn ${HOME}/.android/crystax-ndk ${HOME}/.buildozer/

COPY . ${WORK_DIR}
