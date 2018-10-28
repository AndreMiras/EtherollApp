# EtherollApp

[![Build Status](https://secure.travis-ci.org/AndreMiras/EtherollApp.png?branch=develop)](http://travis-ci.org/AndreMiras/EtherollApp)

<a href="https://github.com/AndreMiras/EtherollApp/releases/download/v20181028/etheroll-2018.1028-debug.apk"><img src="https://www.scottishchildrenslottery.com/export/system/modules/com.assense.gaming.stv.template/resources/images/google-play-store.svg" width="200"></a>

Provably fair dice game running on the [Ethereum blockchain](https://etheroll.com/#/smart-contract).
Built with Python, [Kivy](https://github.com/kivy/kivy) and love.

<img src="https://i.imgur.com/ORa0iTG.png" alt="Screenshot mainscreen" width="300"> <img src="https://i.imgur.com/Imwuifi.png" alt="Screenshot roll history" width="300">

## Run
```
. venv/bin/activate
./src/main.py
```

## Install
```
make
```

## Test
```
make test
make uitest
```

## Docker
There's a [Dockerfile](Dockerfile) to build Linux dependencies and run tests.
```
docker build --tag=etheroll .
docker run etheroll /bin/sh -c '. venv/bin/activate && make test'
```
