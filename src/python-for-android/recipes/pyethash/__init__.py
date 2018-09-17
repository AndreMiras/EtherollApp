import os
from pythonforandroid.recipe import PythonRecipe


class PyethashRecipe(PythonRecipe):
    version = '0.1.27'
    url = 'https://pypi.python.org/packages/source/p/pyethash/pyethash-{version}.tar.gz'
    depends = [('python2', 'python3crystax'), 'setuptools']

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super(PyethashRecipe, self).get_recipe_env(arch, with_flags_in_cc)
        # CFLAGS may only be used to specify C compiler flags, for macro definitions use CPPFLAGS
        env['CPPFLAGS'] = env['CFLAGS']
        env['CFLAGS'] = ''
        # LDFLAGS may only be used to specify linker flags, for libraries use LIBS
        env['LDFLAGS'] = env['LDFLAGS'].replace('-lm', '').replace('-lcrystax', '')
        env['LDFLAGS'] += ' -L{}'.format(os.path.join(self.ctx.bootstrap.build_dir, 'libs', arch.arch))
        env['LIBS'] = ' -lm'
        if self.ctx.ndk == 'crystax':
            env['LIBS'] += ' -lcrystax -lpython{}m'.format(self.ctx.python_recipe.version[0:3])
        env['LDSHARED'] += env['LIBS']
        return env


recipe = PyethashRecipe()
