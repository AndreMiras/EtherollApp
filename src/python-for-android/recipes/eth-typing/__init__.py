from pythonforandroid.recipe import PythonRecipe


class EthTypingRecipe(PythonRecipe):
    version = '2.0.0'
    url = 'https://github.com/ethereum/eth-typing/archive/v{version}.tar.gz'
    depends = [('python2', 'python3crystax'), 'setuptools']
    patches = ['setup.patch']


recipe = EthTypingRecipe()
