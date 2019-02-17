import os
from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class LruDictRecipe(CompiledComponentsPythonRecipe):
    version = '1.1.5'
    url = 'https://github.com/amitdev/lru-dict/archive/v{version}.tar.gz'
    depends = ['setuptools']
    call_hostpython_via_targetpython = False


recipe = LruDictRecipe()
