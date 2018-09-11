# iOS support

## Current status
iOS is currently not supported, but there're plans to do so, see
[AndreMiras/EtherollApp#37](https://github.com/AndreMiras/EtherollApp/issues/37).

## Build
```sh
buildozer ios debug
```

## Virtual Machine
Currently running through a Virtual Machine from
[AndrewDryga/vagrant-box-osx](https://github.com/AndrewDryga/vagrant-box-osx).

## Troubleshoot
```
xcode-select: error: tool 'xcodebuild' requires Xcode, but active developer directory '/Library/Developer/CommandLineTools' is a command line tools instance
```
This is because `xcode-select` is pointing to the wrong developer directory.
Fix with:
```sh
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
```
More info: <https://stackoverflow.com/a/17980786/185510>
