# Docker image for installing dependencies on Linux and running tests.
# Build with:
# docker build --tag=andremiras/etherollapp-linux --file=dockerfiles/Dockerfile-linux .
# Run with:
# docker run andremiras/etherollapp-linux /bin/sh -c 'make test'
# Or using the entry point shortcut:
# docker run andremiras/etherollapp-linux 'make test'
# Or for interactive shell:
# docker run -it --rm andremiras/etherollapp-linux
# For running UI:
# xhost +"local:docker@"
# docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix andremiras/etherollapp-linux 'make uitest'
FROM ubuntu:18.04

ENV USER="user"
ENV HOME_DIR="/home/${USER}"
ENV WORK_DIR="${HOME_DIR}/app"

# configure locale
RUN apt update -qq > /dev/null && apt install -qq --yes --no-install-recommends \
    locales && \
    locale-gen en_US.UTF-8 && \
    rm -rf /var/lib/apt/lists/*
ENV LANG="en_US.UTF-8" \
    LANGUAGE="en_US.UTF-8" \
    LC_ALL="en_US.UTF-8"

# install system dependencies
RUN apt update -qq > /dev/null && apt install -qq --yes --no-install-recommends \
    lsb-release \
    make \
    sudo && \
    rm -rf /var/lib/apt/lists/*

# prepare non root env, with sudo access and no password
RUN useradd --create-home --home-dir ${HOME_DIR} --shell /bin/bash ${USER} && \
    usermod -append --groups sudo ${USER} && \
    echo "%sudo ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

USER ${USER}

# install system dependencies
COPY Makefile /tmp/Makefile
RUN sudo make --file /tmp/Makefile system_dependencies_linux && \
    sudo rm /tmp/Makefile && \
    sudo rm -rf /var/lib/apt/lists/* && \
    mkdir ${WORK_DIR}

WORKDIR ${WORK_DIR}
COPY . ${WORK_DIR}
# required by Kivy `App.user_data_dir`
RUN mkdir ~/.config
ENTRYPOINT ["./dockerfiles/start.sh"]
