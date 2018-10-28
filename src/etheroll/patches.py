import ctypes.util
import os
from ctypes.util import find_library as original_find_library

from kivy.utils import platform


def find_library(name):
    """
    Looks in the right places on Android, see:
    https://github.com/kivy/python-for-android/blob/0.6.0/
    pythonforandroid/recipes/python2/patches/ctypes-find-library-updated.patch
    """
    # Check the user app lib dir
    app_root = os.path.abspath('../../').split(os.path.sep)
    lib_search = os.path.sep.join(app_root) + os.path.sep + 'lib'
    for filename in os.listdir(lib_search):
        if filename.endswith('.so') and name in filename:
            return lib_search + os.path.sep + filename
    # Check the normal Android system libraries
    for filename in os.listdir('/system/lib'):
        if filename.endswith('.so') and name in filename:
            return lib_search + os.path.sep + filename
    # fallback on the original find_library()
    return original_find_library(name)


def patch_find_library_android():
    """
    Monkey patches find_library() to first try to find libraries on Android.
    https://github.com/AndreMiras/EtherollApp/issues/30
    """
    if platform == 'android':
        ctypes.util.find_library = find_library
