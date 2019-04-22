# How to release

This is documenting the release process.


## Git flow & CHANGELOG.md

Make sure the CHANGELOG.md is up to date and follows the http://keepachangelog.com guidelines.
Start the release with git flow:
```sh
git flow release start vYYYYMMDD
```
Now update the [CHANGELOG.md](/src/CHANGELOG.md) `[Unreleased]` section to match the new release version.
Also update the `__version__` and `__version_code__` values from the [version.py](/src/version.py) file.
Optionally already update the direct download link from the [README.md](/README.md).
Then commit and finish release.
```sh
git commit -a -m "vYYYYMMDD"
git flow release finish
```
Push everything, make sure tags are also pushed:
```sh
git push
git push origin master:master
git push --tags
```

## GitHub

Got to GitHub [Release/Tags](https://github.com/AndreMiras/EtherollApp/tags), click "Add release notes" for the tag just created.
Add the tag name in the "Release title" field and the relevant CHANGELOG.md section in the "Describe this release" textarea field.
Finally, attach the generated APK release file and click "Publish release".
