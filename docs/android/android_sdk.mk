# Downloads and installs the Android SDK
# Tested under Ubuntu 18.04 Bionic

# latest version from https://developer.android.com/studio/index.html
ANDROID_SDK_TOOLS_VERSION=3859397
ANDROID_HOME=$(HOME)/.android
ANDROID_SDK_HOME=$(ANDROID_HOME)/android-sdk
ANDROID_SDK_TOOLS_ARCHIVE=sdk-tools-linux-$(ANDROID_SDK_TOOLS_VERSION).zip
ANDROID_SDK_TOOLS_DL_URL=https://dl.google.com/android/repository/$(ANDROID_SDK_TOOLS_ARCHIVE)


all: download_android_sdk extract_android_sdk update_android_sdk

download_android_sdk:
	curl --location --progress-bar --continue-at - \
	$(ANDROID_SDK_TOOLS_DL_URL) --output $(ANDROID_SDK_TOOLS_ARCHIVE)

extract_android_sdk:
	mkdir --parents $(ANDROID_SDK_HOME)
	unzip -q $(ANDROID_SDK_TOOLS_ARCHIVE) -d $(ANDROID_SDK_HOME)

# updates Android SDK, install Android API, Build Tools...
update_android_sdk:
	mkdir --parents $(HOME)/.android
	echo '### User Sources for Android SDK Manager' > $(HOME)/.android/repositories.cfg
	yes | $(ANDROID_SDK_HOME)/tools/bin/sdkmanager --licenses
	$(ANDROID_SDK_HOME)/tools/bin/sdkmanager "platform-tools"
	$(ANDROID_SDK_HOME)/tools/bin/sdkmanager "platforms;android-19"
	$(ANDROID_SDK_HOME)/tools/bin/sdkmanager "build-tools;26.0.2"
