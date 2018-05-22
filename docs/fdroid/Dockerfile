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

# get the latest version from https://www.crystax.net/en/download
ENV CRYSTAX_NDK_VERSION="10.3.2"

ENV ANDROID_HOME="${HOME_DIR}/.buildozer"
ENV CRYSTAX_NDK_HOME="${ANDROID_HOME}/crystax-ndk" \
    ANDROID_SDK_HOME="${ANDROID_HOME}/android/platform/android-sdk-20"
ENV ANDROID_NDK_HOME="${ANDROID_SDK_HOME}/ndk-bundle" \
	CRYSTAX_NDK_HOME_V="${CRYSTAX_NDK_HOME}-${CRYSTAX_NDK_VERSION}"
ENV CRYSTAX_NDK_ARCHIVE="crystax-ndk-${CRYSTAX_NDK_VERSION}-linux-x86_64.tar.xz"
ENV CRYSTAX_NDK_DL_URL="https://eu.crystax.net/download/${CRYSTAX_NDK_ARCHIVE}"
ENV ANDROID_SDK="${ANDROID_SDK_HOME}" \
	ANDROID_NDK="${CRYSTAX_NDK_HOME}"


# prepare non root env
RUN useradd --create-home --shell /bin/bash ${USER}
WORKDIR ${WORK_DIR}
# when login to the container for debugging
RUN echo "root:root" | chpasswd

# configure locale
RUN apt update -qq > /dev/null && apt install --yes --no-install-recommends \
    locales && \
    locale-gen en_US.UTF-8
ENV LANG="en_US.UTF-8" \
    LANGUAGE="en_US.UTF-8" \
    LC_ALL="en_US.UTF-8"

# install system dependencies
RUN apt update -qq > /dev/null && apt install --yes --no-install-recommends \
    python3 python3-pip python3-distutils python3-setuptools git curl wget \
    openjdk-8-jdk zlib1g-dev vim autogen autoconf libtool

# build dependencies
# https://buildozer.readthedocs.io/en/latest/installation.html#android-on-ubuntu-18-04-64bit
RUN dpkg --add-architecture i386 &&  apt update -qq && apt install -qq --yes --no-install-recommends \
        build-essential ccache git libncurses5:i386 libstdc++6:i386 libgtk2.0-0:i386 \
        libpangox-1.0-0:i386 libpangoxft-1.0-0:i386 libidn11:i386 python2.7 python2.7-dev \
        openjdk-8-jdk unzip zlib1g-dev zlib1g:i386

# make python3 the default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1 && \
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

USER ${USER}

# download and install CrystaX NDK
# added `gnutls_handshake` flag to workaround random `gnutls_handshake()` issues
RUN curl --location --progress-bar "${CRYSTAX_NDK_DL_URL}" --output "${CRYSTAX_NDK_ARCHIVE}" --insecure && \
	mkdir -p "${ANDROID_HOME}"
RUN tar -xf "${CRYSTAX_NDK_ARCHIVE}" --directory "${ANDROID_HOME}" \
    --exclude=crystax-ndk-${CRYSTAX_NDK_VERSION}/docs \
    --exclude=crystax-ndk-${CRYSTAX_NDK_VERSION}/samples \
    --exclude=crystax-ndk-${CRYSTAX_NDK_VERSION}/tests \
    --exclude=crystax-ndk-${CRYSTAX_NDK_VERSION}/toolchains/renderscript \
    --exclude=crystax-ndk-${CRYSTAX_NDK_VERSION}/toolchains/x86_64-* \
    --exclude=crystax-ndk-${CRYSTAX_NDK_VERSION}/toolchains/llvm-* \
    --exclude=crystax-ndk-${CRYSTAX_NDK_VERSION}/toolchains/aarch64-* \
    --exclude=crystax-ndk-${CRYSTAX_NDK_VERSION}/toolchains/mips64el-*
RUN ln -sfn "${CRYSTAX_NDK_HOME_V}" "${CRYSTAX_NDK_HOME}"

# install fdroidserver and fdroiddata
RUN pip install fdroidserver
RUN curl --location --progress-bar "${FDROIDDATA_DL_URL}" --output "${FDROIDDATA_ARCHIVE}" && \
    tar -xf "${FDROIDDATA_ARCHIVE}" --directory "${WORK_DIR}"

# install buildozer and dependencies
RUN pip install Cython==0.25.2 buildozer

WORKDIR ${WORK_DIR}
