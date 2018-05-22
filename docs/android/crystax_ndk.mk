# Downloads and installs the CrystaX NDK
# Tested under Ubuntu 18.04 Bionic

# latest version from https://www.crystax.net/en/download
CRYSTAX_NDK_VERSION=10.3.2
ANDROID_HOME=$(HOME)/.android
CRYSTAX_NDK_HOME=$(ANDROID_HOME)/crystax-ndk
CRYSTAX_NDK_HOME_V=$(CRYSTAX_NDK_HOME)-$(CRYSTAX_NDK_VERSION)
CRYSTAX_NDK_ARCHIVE=crystax-ndk-$(CRYSTAX_NDK_VERSION)-linux-x86_64.tar.xz
CRYSTAX_NDK_DL_URL=https://eu.crystax.net/download/$(CRYSTAX_NDK_ARCHIVE)


all: download_crystax_ndk extract_crystax_ndk

download_crystax_ndk:
	curl --location --progress-bar $(CRYSTAX_NDK_DL_URL) --output $(CRYSTAX_NDK_ARCHIVE)

extract_crystax_ndk:
	mkdir -p $(ANDROID_HOME)
	tar -xf $(CRYSTAX_NDK_ARCHIVE) --directory $(ANDROID_HOME) \
	    --exclude=crystax-ndk-$(CRYSTAX_NDK_VERSION)/docs \
	    --exclude=crystax-ndk-$(CRYSTAX_NDK_VERSION)/samples \
	    --exclude=crystax-ndk-$(CRYSTAX_NDK_VERSION)/tests \
	    --exclude=crystax-ndk-$(CRYSTAX_NDK_VERSION)/toolchains/renderscript \
	    --exclude=crystax-ndk-$(CRYSTAX_NDK_VERSION)/toolchains/x86_64-* \
	    --exclude=crystax-ndk-$(CRYSTAX_NDK_VERSION)/toolchains/llvm-* \
	    --exclude=crystax-ndk-$(CRYSTAX_NDK_VERSION)/toolchains/aarch64-* \
	    --exclude=crystax-ndk-$(CRYSTAX_NDK_VERSION)/toolchains/mips64el-*
	ln -sfn $(CRYSTAX_NDK_HOME_V) $(CRYSTAX_NDK_HOME)
