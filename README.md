# EtherollApp

[![Build Status](https://secure.travis-ci.org/AndreMiras/EtherollApp.png?branch=develop)](http://travis-ci.org/AndreMiras/EtherollApp)
[![PyPI version](https://badge.fury.io/py/EtherollApp.svg)](https://badge.fury.io/py/EtherollApp)
[![Get it on F-Droid](https://img.shields.io/f-droid/v/com.github.andremiras.etheroll.svg)](https://f-droid.org/en/packages/com.github.andremiras.etheroll)
[![Releases](https://img.shields.io/github/release/andremiras/EtherollApp.svg?logo=github)](https://github.com/AndreMiras/EtherollApp/releases)

<a href="https://f-droid.org/packages/com.github.andremiras.etheroll">
  <img src="https://fdroid.gitlab.io/artwork/badge/get-it-on.png" height="75">
</a>
<a href="https://github.com/AndreMiras/EtherollApp/releases/tag/v2019.1108">
  <img src="https://www.livenettv.to/img/landing-page-1/google-play.png" height="75">
</a>

Provably fair dice game running on the [Ethereum blockchain](https://etheroll.com/#/smart-contract).
Built with Python, [Kivy](https://github.com/kivy/kivy) and love.

<img src="https://i.imgur.com/ORa0iTG.png" alt="Screenshot mainscreen" width="300"> <img src="https://i.imgur.com/Imwuifi.png" alt="Screenshot roll history" width="300">


## Install & Usage
[EtherollApp is available on PyPI](https://pypi.org/project/EtherollApp/).
Therefore it can be installed via `pip`.
```sh
pip3 install --user EtherollApp
```
Once installed, it should be available in your `PATH` and can be ran from the command line.
```sh
etherollapp
```

## Develop & Contribute
If you want to experiment with the project or contribute, you can clone it and install dependencies.
```sh
make
```
Later run the code on desktop via the `run` target.
```sh
make run
```
Unit tests are also available.
```sh
make test
make uitest
```
On Android you can build, deploy and run using [Buildozer](https://github.com/kivy/buildozer).
```sh
buildozer android debug deploy run logcat
```
And debug with `logcat`.
```sh
buildozer android adb -- logcat
```
