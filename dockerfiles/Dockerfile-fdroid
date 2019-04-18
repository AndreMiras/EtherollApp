# Docker image for running F-Droid build scripts.
# Build with:
#   docker build --tag=fdroid --file=dockerfiles/Dockerfile-fdroid .
# Run with:
#   docker run fdroid /bin/sh -c 'fdroid build -v -l com.github.andremiras.etheroll'
# Or using the entry point shortcut:
#   docker run fdroid 'fdroid build -v -l com.github.andremiras.etheroll'
# Or for interactive shell:
#   docker run -it --rm fdroid
# WARNING:
# The `--on-server` option should only be used in a container since it could
# could mess up with the system it's running in.
#
FROM debian:stretch

ENV USER="user"
ENV HOME_DIR="/home/${USER}"
ENV WORK_DIR="${HOME_DIR}" \
    PATH="${HOME_DIR}/.local/bin:${PATH}" \
    FDROIDDATA_ARCHIVE="fdroiddata-feature-new_app_etheroll.tar.bz2"
    # FDROIDDATA_ARCHIVE="fdroiddata-master.tar.bz2"
ENV FDROIDDATA_DL_URL="https://gitlab.com/fdroid/fdroiddata/-/archive/master/${FDROIDDATA_ARCHIVE}"
# fdroid requires this env, see:
# https://gitlab.com/fdroid/fdroidserver/merge_requests/290
ENV ANDROID_HOME="${HOME_DIR}/.android"

ENV DOCKERFILES_VERSION="master" \
    DOCKERFILES_URL="https://raw.githubusercontent.com/AndreMiras/dockerfiles"
ENV MAKEFILES_URL="${DOCKERFILES_URL}/${DOCKERFILES_VERSION}/buildozer_android_new"


# configure locale
RUN apt update -qq > /dev/null && apt install --yes --no-install-recommends \
    locales && \
    locale-gen en_US.UTF-8
ENV LANG="C.UTF-8" \
    LANGUAGE="C.UTF-8" \
    LC_ALL="C.UTF-8"
RUN dpkg-reconfigure --frontend noninteractive locales


# install fdroid basebox dependencies, refs:
# https://gitlab.com/fdroid/basebox/blob/0.5.1/fdroid_basebox.py#L80
# https://gitlab.com/fdroid/fdroidserver/blob/1.1.1/buildserver/provision-apt-get-install#L45
RUN apt install -qq --yes --no-install-recommends \
    autoconf \
    automake \
    ca-certificates \
    curl \
    git \
    lbzip2 \
    libpython3-dev \
    libtool \
    make \
    openjdk-8-jdk \
    python3 \
    python3-pip \
    python3-setuptools \
    sudo \
    unzip \
    zip

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

# downloads and installs Android SDK
RUN curl --location --progress-bar ${MAKEFILES_URL}/android_sdk.mk --output android_sdk.mk
RUN make -f android_sdk.mk

# install fdroidserver and fdroiddata
RUN pip install fdroidserver
RUN curl --location --progress-bar "${FDROIDDATA_DL_URL}" --output "${FDROIDDATA_ARCHIVE}" && \
    tar -xf "${FDROIDDATA_ARCHIVE}" --directory "${WORK_DIR}"

WORKDIR ${WORK_DIR}
