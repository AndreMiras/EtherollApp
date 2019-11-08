from pythonforandroid.recipe import PythonRecipe


class EthAccountRecipe(PythonRecipe):
    """
    This recipes is a workaround to build on F-Droid build server.
    Their build server doesn't have Python3.6 yet, hence we want to force this
    recipe to build on the compiled host Python, refs:
    https://github.com/AndreMiras/EtherollApp/issues/167
    """
    version = '0.4.0'
    url = (
        'https://pypi.python.org/packages/source/e/eth-account/'
        'eth-account-{version}.tar.gz'
    )
    depends = ['setuptools']
    patches = ['setup.py.patch']
    call_hostpython_via_targetpython = False


recipe = EthAccountRecipe()
