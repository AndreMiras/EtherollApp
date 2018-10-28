[app]

# (str) Title of your application
title = Etheroll

# (str) Package name
package.name = etheroll

# (str) Package domain (needed for android/ios packaging)
package.domain = com.github.andremiras

# (str) Source code where the main.py live
source.dir = src

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,md,json

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
#source.exclude_dirs = tests, bin
source.exclude_dirs = python-for-android

# (list) List of exclusions using pattern matching
#source.exclude_patterns = license,images/*/*.jpg

# (str) Application versioning (method 1)
# version = 0.1

# (str) Application versioning (method 2)
version.regex = __version__ = ['"](.*)['"]
version.filename = %(source.dir)s/version.py

# (list) Application requirements
# comma seperated e.g. requirements = sqlite3,kivy
requirements =
    hostpython3crystax==3.6,
    python3crystax==3.6,
    setuptools,
    kivy==1.10.1,
    plyer==1.3.1,
    oscpy==0.3.0,
    android,
    gevent,
    cffi,
    https://github.com/AndreMiras/KivyMD/archive/9b2206a.tar.gz,
    openssl,
    pyelliptic==1.5.7,
    asn1crypto==0.24.0,
    coincurve==7.1.0,
    bitcoin==1.1.42,
    devp2p==0.9.3,
    pycryptodome==3.4.6,
    pbkdf2==1.3,
    py-ecc==1.4.2,
    pysha3==1.0.2,
    pyyaml==3.12,
    scrypt==0.8.6,
    ethereum==2.1.1,
    ptyprocess==0.5.2,
    pexpect==4.4.0,
    Pygments==2.2.0,
    decorator==4.2.1,
    ipython-genutils==0.2.0,
    traitlets==4.3.2,
    ipython==5.5.0,
    click==6.7,
    pickleshare==0.7.4,
    simplegeneric==0.8.1,
    wcwidth==0.1.7,
    prompt-toolkit==1.0.15,
    https://github.com/ethereum/pyethapp/archive/8406f32.zip,
    idna==2.6,
    typing==3.6.4,
    eth-keys==0.2.0b3,
    eth-keyfile==0.5.1,
    rlp==0.6.0,
    eth-rlp==0.1.2,
    attrdict==2.0.0,
    eth-account==0.2.2,
    hexbytes==0.1.0,
    lru-dict==1.1.5,
    web3==4.0.0b11,
    certifi==2018.1.18,
    chardet==3.0.4,
    urllib3==1.22,
    requests==2.18.4,
    https://github.com/corpetty/py-etherscan-api/archive/cb91fb3.zip,
    eth-testrpc==1.3.3,
    eth-hash==0.1.1,
    pyethash==0.1.27,
    cytoolz==0.9.0,
    toolz==0.9.0,
    eth-abi==1.0.0,
    eth-utils==1.0.1,
    raven==6.6.0,
    requests-cache==0.4.13,
    qrcode,
    https://github.com/AndreMiras/garden.layoutmargin/archive/20180517.zip

# (str) Custom source folders for requirements
# Sets custom source for any requirements with recipes
# requirements.source.kivy = ../../kivy

# (list) Garden requirements
#garden_requirements =
garden_requirements = qrcode

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png
presplash.filename = docs/images/etheroll-logo.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png
icon.filename = docs/images/icon.png

# (str) Supported orientation (one of landscape, portrait or all)
orientation = portrait

# (list) List of service to declare
#services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY
services = service:service/main.py

#
# OSX Specific
#

#
# author = © Copyright Info

# change the major version of python used by the app
osx.python_version = 3

# Kivy version to use
osx.kivy_version = 1.9.1

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Presplash background color (for new android toolchain)
# Supported formats are: #RRGGBB #AARRGGBB or one of the following names:
# red, blue, green, black, white, gray, cyan, magenta, yellow, lightgray,
# darkgray, grey, lightgrey, darkgrey, aqua, fuchsia, lime, maroon, navy,
# olive, purple, silver, teal.
#android.presplash_color = #FFFFFF

# (list) Permissions
#android.permissions = INTERNET
android.permissions = INTERNET

# (int) Android API to use
#android.api = 19

# (int) Minimum API required
#android.minapi = 9

# (int) Android SDK version to use
#android.sdk = 20

# (str) Android NDK version to use
#android.ndk = 9c
# android.ndk = 10

# (bool) Use --private data storage (True) or --dir public storage (False)
#android.private_storage = True

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
#android.ndk_path =
android.ndk_path = ~/.buildozer/crystax-ndk

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
#android.sdk_path =

# (str) ANT directory (if empty, it will be automatically downloaded.)
#android.ant_path =

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time
# when an update is due and you just want to test/build your package
# android.skip_update = False

# (str) Android entry point, default is ok for Kivy-based app
#android.entrypoint = org.renpy.android.PythonActivity

# (list) Pattern to whitelist for the whole project
#android.whitelist =

# (str) Path to a custom whitelist file
#android.whitelist_src =
# android.whitelist_src = whitelist.txt

# (str) Path to a custom blacklist file
#android.blacklist_src =
android.blacklist_src = blacklist.txt

# (list) List of Java .jar files to add to the libs so that pyjnius can access
# their classes. Don't add jars that you do not need, since extra jars can slow
# down the build process. Allows wildcards matching, for example:
# OUYA-ODK/libs/*.jar
#android.add_jars = foo.jar,bar.jar,path/to/more/*.jar

# (list) List of Java files to add to the android project (can be java or a
# directory containing the files)
#android.add_src =

# (list) Android AAR archives to add (currently works only with sdl2_gradle
# bootstrap)
#android.add_aars =

# (list) Gradle dependencies to add (currently works only with sdl2_gradle
# bootstrap)
#android.gradle_dependencies =

# (str) python-for-android branch to use, defaults to master
#p4a.branch = stable
p4a.branch = master

# (str) OUYA Console category. Should be one of GAME or APP
# If you leave this blank, OUYA support will not be enabled
#android.ouya.category = GAME

# (str) Filename of OUYA Console icon. It must be a 732x412 png image.
#android.ouya.icon.filename = %(source.dir)s/data/ouya_icon.png

# (str) XML file to include as an intent filters in <activity> tag
#android.manifest.intent_filters =

# (list) Android additionnal libraries to copy into libs/armeabi
#android.add_libs_armeabi = libs/android/*.so
#android.add_libs_armeabi_v7a = libs/android-v7/*.so
#android.add_libs_x86 = libs/android-x86/*.so
#android.add_libs_mips = libs/android-mips/*.so

# (bool) Indicate whether the screen should stay on
# Don't forget to add the WAKE_LOCK permission if you set this to True
#android.wakelock = False

# (list) Android application meta-data to set (key=value format)
#android.meta_data =

# (list) Android library project to add (will be added in the
# project.properties automatically.)
#android.library_references =

# (str) Android logcat filters to use
#android.logcat_filters = *:S python:D

# (bool) Copy library instead of making a libpymodules.so
#android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86
android.arch = armeabi-v7a

#
# Python for android (p4a) specific
#

# (str) python-for-android git clone directory (if empty, it will be automatically cloned from github)
#p4a.source_dir =

# (str) The directory in which python-for-android should look for your own build recipes (if any)
#p4a.local_recipes =
p4a.local_recipes = %(source.dir)s/python-for-android/recipes/

# (str) Filename to the hook for p4a
#p4a.hook =

# (str) Bootstrap to use for android builds
# p4a.bootstrap = sdl2


#
# iOS specific
#

# (str) Path to a custom kivy-ios folder
#ios.kivy_ios_dir = ../kivy-ios

# (str) Name of the certificate to use for signing the debug version
# Get a list of available identities: buildozer ios list_identities
#ios.codesign.debug = "iPhone Developer: <lastname> <firstname> (<hexstring>)"
ios.codesign.debug = "iPhone Developer: andre.miras@gmail.com (9BF7W3M52N)"

# (str) Name of the certificate to use for signing the release version
#ios.codesign.release = %(ios.codesign.debug)s
ios.codesign.release = %(ios.codesign.debug)s


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .ipa) storage
# bin_dir = ./bin

#    -----------------------------------------------------------------------------
#    List as sections
#
#    You can define all the "list" as [section:key].
#    Each line will be considered as a option to the list.
#    Let's take [app] / source.exclude_patterns.
#    Instead of doing:
#
#[app]
#source.exclude_patterns = license,data/audio/*.wav,data/images/original/*
#
#    This can be translated into:
#
#[app:source.exclude_patterns]
#license
#data/audio/*.wav
#data/images/original/*
#


#    -----------------------------------------------------------------------------
#    Profiles
#
#    You can extend section / key with a profile
#    For example, you want to deploy a demo version of your application without
#    HD content. You could first change the title to add "(demo)" in the name
#    and extend the excluded directories to remove the HD content.
#
#[app@demo]
#title = My Application (demo)
#
#[app:source.exclude_patterns@demo]
#images/hd/*
#
#    Then, invoke the command line with the "demo" profile:
#
#buildozer --profile demo android debug
