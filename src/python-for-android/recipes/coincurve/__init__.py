import os
from pythonforandroid.recipe import PythonRecipe


class CoincurveRecipe(PythonRecipe):
    version = '7.1.0'
    url = 'https://github.com/ofek/coincurve/archive/{version}.tar.gz'
    call_hostpython_via_targetpython = False
    depends = [('python2', 'python3crystax'), 'setuptools',
        'libffi', 'cffi', 'libsecp256k1']
    patches = [
        "cross_compile.patch", "drop_setup_requires.patch",
        "find_lib.patch", "no-download.patch"]

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super(CoincurveRecipe, self).get_recipe_env(arch, with_flags_in_cc)
        libsecp256k1 = self.get_recipe('libsecp256k1', self.ctx)
        libsecp256k1_dir = libsecp256k1.get_build_dir(arch.arch)
        env['CFLAGS'] += ' -I' + os.path.join(libsecp256k1_dir, 'include')
        # required additional library and path for Crystax
        if self.ctx.ndk == 'crystax':
            # only keeps major.minor (discards patch)
            python_version = self.ctx.python_recipe.version[0:3]
            ndk_dir_python = os.path.join(self.ctx.ndk_dir, 'sources/python/', python_version)
            env['LDFLAGS'] += ' -L{}'.format(os.path.join(ndk_dir_python, 'libs', arch.arch))
            env['LDFLAGS'] += ' -lpython{}m'.format(python_version)
        env['LDFLAGS'] += " -lsecp256k1"
        return env


recipe = CoincurveRecipe()

