# Troubleshoot


## Android

### Devices no permission
When running the adb devices command, if you're getting a "no permissions" error message like below:
```
buildozer android adb -- devices
...
List of devices attached 
????????????    no permissions
```

Update your udev rules, there's an example to adapt to your Android device here:
```
sudo cp root/etc/udev/rules.d/51-android.rules /etc/udev/rules.d/
```
Then replug your device and rerun the command.


### Devices unauthorized
When running the adb devices command, if you're getting a "unauthorized" error message like below:
```
buildozer android adb -- devices
...
List of devices attached 
X9LDU14B18003251        unauthorized
```
Then you simply need to allow your dev computer from your Android device.


### Buildozer run

Buildozer fails with the error below when installing dependencies:
```
urllib.error.URLError: <urlopen error unknown url type: https>
```
First install `libssl-dev`:
```
sudo apt install libssl-dev
```
Then clean openssl recipe build and retry:
```
buildozer android p4a -- clean_recipe_build openssl
buildozer android debug
```


Buildozer fails when building libffi:
```
configure.ac:41: error: possibly undefined macro: AC_PROG_LIBTOOL
      If this token and others are legitimate, please use m4_pattern_allow.
      See the Autoconf documentation.
autoreconf: /usr/bin/autoconf failed with exit status: 1
```
Fix it by installing autogen autoconf and libtool:
```
sudo apt install autogen autoconf libtool
```

Buildozer fails with when building cffi:
```
c/_cffi_backend.c:13:17: fatal error: ffi.h: No such file or directory
```
Try installing `libffi-dev`:
```
sudo apt install libffi-dev
```
If it doesn't solve the issue, it might be related to another problem, see:
https://github.com/kivy/python-for-android/issues/1148


Building with `javac`:
```
(use -source 7 or higher to enable multi-catch statement)
```
Edit: `~/.buildozer/android/platform/android-sdk-20/tools/ant/build.xml` file
and change:
```
<property name="java.target" value="1.5" />
<property name="java.source" value="1.5" />
```
to:
```
<property name="java.target" value="7" />
<property name="java.source" value="7" />
```

Buildozer fails at copying APK to current directory:
```
IOError: [Errno 2] No such file or directory: u'/home/andre/workspace/EtherollApp/.buildozer/android/platform/build/dists/etheroll/build/outputs/apk/etheroll-debug.apk'
```
See https://github.com/AndreMiras/EtherollApp/issues/26
To (dirty) workaround it, edit `~/.local/lib/python2.7/site-packages/buildozer/targets/android.py`
and change:
```
if is_gradle_build:
```
by:
```
if not is_gradle_build:
```



## Kivy

### Debugging widget sizes

<https://github.com/kivy/kivy/wiki/Debugging-widget-sizes>
