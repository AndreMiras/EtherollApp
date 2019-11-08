from pythonforandroid.recipe import PythonRecipe


class Web3Recipe(PythonRecipe):
    """
    This recipes is a workaround to build on F-Droid build server.
    Their build server doesn't have Python3.6 yet, hence we want to force this
    recipe to build on the compiled host Python, refs:
    https://github.com/AndreMiras/EtherollApp/issues/167
    """
    version = 'web3==5.2.0'
    url = (
        'https://pypi.python.org/packages/source/w/web3/'
        'web3-{version}.tar.gz'
    )
    depends = ['setuptools']
    call_hostpython_via_targetpython = False


recipe = Web3Recipe()
