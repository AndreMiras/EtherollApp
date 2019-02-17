import os
from pythonforandroid.recipe import CythonRecipe


class CytoolzRecipe(CythonRecipe):
    version = '0.9.0'
    url = 'https://github.com/pytoolz/cytoolz/archive/{version}.tar.gz'
    depends = ['setuptools']

recipe = CytoolzRecipe()
