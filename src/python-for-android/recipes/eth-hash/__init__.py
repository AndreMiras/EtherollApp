from pythonforandroid.recipe import PythonRecipe


class EthHashRecipe(PythonRecipe):
    version = '0.2.0'
    url = 'https://github.com/ethereum/eth-hash/archive/v{version}.tar.gz'
    depends = [('python2', 'python3crystax'), 'setuptools']
    patches = ['disable-setuptools-markdown.patch']


recipe = EthHashRecipe()
