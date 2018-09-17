import os
from pythonforandroid.recipe import PythonRecipe


class PycryptodomeRecipe(PythonRecipe):
    version = '3.4.6'
    url = 'https://github.com/Legrandin/pycryptodome/archive/v{version}.tar.gz'
    depends = [('python2', 'python3crystax'), 'setuptools', 'cffi']
    patches = ['setup.py.patch']

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super(PycryptodomeRecipe, self).get_recipe_env(arch, with_flags_in_cc)
        env['LDFLAGS'] += ' -L{}'.format(os.path.join(self.ctx.bootstrap.build_dir, 'libs', arch.arch))
        return env


recipe = PycryptodomeRecipe()
