# EtherollApp

[![Build Status](https://secure.travis-ci.org/AndreMiras/EtherollApp.png?branch=develop)](http://travis-ci.org/AndreMiras/EtherollApp)

<a href="https://f-droid.org/en/packages/com.github.andremiras.etheroll">
  <img src="https://f-droid.org/badge/get-it-on.png" height="75">
</a>
<a href="https://github.com/AndreMiras/EtherollApp/releases/download/v20190418/etheroll-2019.0418-debug.apk">
  <img src="https://www.livenettv.to/img/landing-page-1/google-play.png" height="75">
</a>

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
