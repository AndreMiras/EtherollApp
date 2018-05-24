# Docker image for running F-Droid build scripts.
# Build with:
# docker build --tag=fdroid .
# Run with:
# docker run fdroid /bin/sh -c 'fdroid build -v -l com.github.andremiras.etheroll'
# Or for interactive shell:
# docker run -it --rm fdroid
FROM ubuntu:18.04

ENV USER="user"
ENV HOME_DIR="/home/${USER}"
ENV WORK_DIR="${HOME_DIR}" \
    PATH="${HOME_DIR}/.local/bin:${PATH}" \
    FDROIDDATA_ARCHIVE="fdroiddata-master.tar.bz2"
ENV FDROIDDATA_DL_URL="https://gitlab.com/fdroid/fdroiddata/-/archive/master/${FDROIDDATA_ARCHIVE}"
# currently needed because buildozer still uses `tools/android` binary
# even though we have the new `tools/bin/sdkmanager` available
ENV USE_SDK_WRAPPER=true

ENV ANDROID_HOME="${HOME_DIR}/.buildozer"
ENV CRYSTAX_NDK_HOME="${ANDROID_HOME}/crystax-ndk" \
    ANDROID_SDK_HOME="${ANDROID_HOME}/android/platform/android-sdk-20"
ENV ANDROID_NDK_HOME="${ANDROID_SDK_HOME}/ndk-bundle" \
	CRYSTAX_NDK_HOME_V="${CRYSTAX_NDK_HOME}-${CRYSTAX_NDK_VERSION}"
ENV CRYSTAX_NDK_ARCHIVE="crystax-ndk-${CRYSTAX_NDK_VERSION}-linux-x86_64.tar.xz"
ENV CRYSTAX_NDK_DL_URL="https://eu.crystax.net/download/${CRYSTAX_NDK_ARCHIVE}"
ENV ANDROID_SDK="${ANDROID_SDK_HOME}" \
	ANDROID_NDK="${CRYSTAX_NDK_HOME}"
ENV DOCKERFILES_VERSION="master" \
    DOCKERFILES_URL="https://raw.githubusercontent.com/AndreMiras/dockerfiles"
ENV MAKEFILES_URL="${DOCKERFILES_URL}/${DOCKERFILES_VERSION}/buildozer_android_new"


# configure locale
RUN apt update -qq > /dev/null && apt install --yes --no-install-recommends \
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
    python3.6 libpython3.6-dev python3-setuptools python3-pip \
    autoconf automake libtool libltdl-dev libffi-dev

# make python3 the default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1 && \
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

# prepare non root env
RUN useradd --create-home --shell /bin/bash ${USER}
# with sudo access and no password
RUN usermod -append --groups sudo ${USER}
RUN echo "%sudo ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

USER ${USER}
WORKDIR ${WORK_DIR}

# downloads and installs CrystaX NDK
RUN curl --location --progress-bar ${MAKEFILES_URL}/crystax_ndk.mk --output crystax_ndk.mk
RUN make -f crystax_ndk.mk ANDROID_HOME=${ANDROID_HOME}

# downloads and installs Android SDK
# TODO ~/.buildozer/android/platform/android-sdk-20/tools/android
RUN curl --location --progress-bar ${MAKEFILES_URL}/android_sdk.mk --output android_sdk.mk
RUN make -f android_sdk.mk ANDROID_SDK_HOME=${ANDROID_SDK_HOME}

# install buildozer and dependencies
RUN curl --location --progress-bar ${MAKEFILES_URL}/buildozer.mk --output buildozer.mk
RUN make -f buildozer.mk

# install fdroidserver and fdroiddata
RUN pip install fdroidserver
RUN curl --location --progress-bar "${FDROIDDATA_DL_URL}" --output "${FDROIDDATA_ARCHIVE}" && \
    tar -xf "${FDROIDDATA_ARCHIVE}" --directory "${WORK_DIR}"

WORKDIR ${WORK_DIR}
