from pythonforandroid.recipe import PythonRecipe


class Web3Recipe(PythonRecipe):
    version = '4.8.1'
    url = 'https://github.com/ethereum/web3.py/archive/v{version}.tar.gz'
    depends = [('python2', 'python3crystax'), 'setuptools']
    patches = ['setup.patch']


recipe = Web3Recipe()
