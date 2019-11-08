# Change Log


## [v2019.1108]

  - Fix Kivy low FPS performances issue
  - Fix 403 errors on Ropsten, refs #156, #157
  - Fix broken F-Droid build, refs #167


## [v2019.1101]

  - Bump Kivy related dependencies
  - Build and CI improvements
  - Transfer out feature, refs #80, #105
  - Migrate to NDK 19b, refs #154
  - Leverage docker image caching refs, #160
  - Docker images size optimizations, refs #161


## [v2019.0911]

  - Update to KivyMD==20181106, refs #144
  - Update to Kivy==1.11.1, refs #148
  - Migrate to Python3.7, refs #147
  - Publish to PyPI, refs #153


## [v2019.0624]

  - Save keystore to private user dir, refs #141
  - Unit test polling service, refs #107
  - Fix `helper_test_roll_history` test, refs #138
  - Simplify service code
  - Unit test settings.py


## [v2019.0426]

  - Support F-Droid auto updates, refs #132
  - Keystore directory and permissions, refs #133, #134


## [v20190418]

  - Fetch minimum bet from contract, refs #129
  - Fix permission issue on settings, refs #131
  - Available on the F-Droid market, refs #36


## [v20190217]

  - Migrate to upstream recipes
  - UI testing in Travis via xvfb, refs #65
  - Split dedicated Etheroll library, refs #97
  - Remove legacy dependencies, refs #122
  - Move to python3 recipe, refs #123
  - Handle write storage permission, refs #125
  - Non root Docker user, refs #127


## [v20181028]

  - Click notification to open the app, refs #114
  - Bets 2nd decimal place precision, refs #116
  - Platform agnostic notification service, refs #120
  - Update balance on roll, refs #115
  - Remove typing patch, refs #72


## [v20180918]

  - Notify when roll processed, refs #57, #103, #106
  - Recipes LDSHARED & CFLAGS cleaning, refs #104
  - Update broken Mainnet node, refs #111
  - Upgrade to Kivy==1.10.1, refs #100


## [v20180911]

  - Fix pycryptodome compilation, refs #99
  - Update to new contract address


## [v20180617]

  - Fix crash when deployed on SD, refs #96


## [v20180531]

  - Handle wrong password error, refs #9
  - Dockerize Android APK compile, refs #38
  - Android CI on Travis, refs #39
  - Prompt error dialog on no network, refs #59
  - Fix crash on empty roll history, refs #67
  - Add xclip & xsel system dependencies, refs #81, #82
  - Load previous screen on back button, refs #84
  - Validate password form on enter key, refs #85
  - Fix settings race condition crash, refs #86
  - Dockerize F-Droid APK compile, refs #89
  - Speed up application loading, refs #91
  - Optional Etherscan API key, refs #93


## [v20180517]

  - Show account balance, refs #8
  - Configurable gas price, refs #23
  - UI improvements, refs #34, #88
  - File split & refactoring, refs #43
  - Lazy screen loading, refs #47, #75
  - Pull to refresh roll history, refs #50, #55
  - Updated contract deployment doc, refs #52
  - UI testing, refs #61, #64
  - Reduce APK size from 26M to 20M, refs #68
  - Run tests from UI, refs #69
  - Ubuntu Bionic 18.04 support, refs #70, #71
  - Show changelog from the app, refs #73
  - Fix scrypt support, refs #76
  - Fix ETH to wei conversion, refs #77
  - Fix test timestamp overflow, refs #78
  - Fix history error on no matching tx, refs #87


## [v20180418]

  - Per account bet history, refs #16
  - Remove topic3 workaround, refs #48
  - Handle unresolved bets, refs #51


## [v20180414]

  - UI testing, refs #10
  - Account creation, refs #13
  - Setup continuous integration, refs #18
  - Dockerized project, refs #19
  - Download ABIs dynamically and cache it, refs #41
  - Show account QR Code, refs #44
  - Quick account actions, refs #45
  - Chances input binding fixes, refs #46


## [v20180405]

  - Switch testnet/mainnet from UI, refs #11, #21
  - Integrate with Sentry, refs #17
  - Android splash screen and icon, refs #24


## [v20180404]

  - Simple account managment refs, #6, #7, #14
  - Porting to Android, refs #12
  - Python3 + greenlet install issue, refs #25
  - Gevent compilation issues, refs #29
  - FileNotFoundError lib crypto on Android, refs #30
  - PyYAML ImportError: No module named 'error', refs #31
  - Android OpenSSL support, refs #32


## [v20180327]

  - Place bet on Testnet, refs #1
  - Simple demo UI, refs #5
