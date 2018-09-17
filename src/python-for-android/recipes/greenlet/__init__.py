import os
from pythonforandroid.recipe import PythonRecipe


class GreenletRecipe(PythonRecipe):
    version = '0.4.9'
    url = 'https://pypi.python.org/packages/source/g/greenlet/greenlet-{version}.tar.gz'
    depends = [('python2', 'python3crystax')]

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super(GreenletRecipe, self).get_recipe_env(arch, with_flags_in_cc)
        # required additional library and path for Crystax
        if self.ctx.ndk == 'crystax':
            # only keeps major.minor (discards patch)
            python_version = self.ctx.python_recipe.version[0:3]
            ndk_dir_python = os.path.join(self.ctx.ndk_dir, 'sources/python/', python_version)
            env['LDFLAGS'] += ' -L{}'.format(os.path.join(ndk_dir_python, 'libs', arch.arch))
            env['LDFLAGS'] += ' -lpython{}m'.format(python_version)
        return env


recipe = GreenletRecipe()
