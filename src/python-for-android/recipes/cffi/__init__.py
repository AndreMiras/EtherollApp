import os
from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class CffiRecipe(CompiledComponentsPythonRecipe):
    name = 'cffi'
    version = '1.4.2'
    url = 'https://pypi.python.org/packages/source/c/cffi/cffi-{version}.tar.gz'

    depends = [('python2', 'python3crystax'), 'setuptools', 'pycparser', 'libffi']

    patches = ['disable-pkg-config.patch']

    # call_hostpython_via_targetpython = False
    install_in_hostpython = True

    def get_recipe_env(self, arch=None):
        env = super(CffiRecipe, self).get_recipe_env(arch)
        # sets linker to use the correct gcc (cross compiler)
        env['LDSHARED'] = env['CC'] + ' -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions'
        libffi = self.get_recipe('libffi', self.ctx)
        includes = libffi.get_include_dirs(arch)
        env['CFLAGS'] = ' -I'.join([env.get('CFLAGS', '')] + includes)
        env['LDFLAGS'] = (env.get('CFLAGS', '') + ' -L' +
                          self.ctx.get_libs_dir(arch.arch))
        env['LDFLAGS'] += ' -L{}'.format(os.path.join(self.ctx.bootstrap.build_dir, 'libs', arch.arch))
        # required for libc and libdl
        ndk_dir = self.ctx.ndk_platform
        ndk_lib_dir = os.path.join(ndk_dir, 'usr', 'lib')
        env['LDFLAGS'] += ' -L{}'.format(ndk_lib_dir)
        env['LDFLAGS'] += " --sysroot={}".format(self.ctx.ndk_platform)
        env['PYTHONPATH'] = ':'.join([
            self.ctx.get_site_packages_dir(),
            env['BUILDLIB_PATH'],
        ])
        return env


recipe = CffiRecipe()
