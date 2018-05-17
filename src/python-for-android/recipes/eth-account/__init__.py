from pythonforandroid.recipe import PythonRecipe


class EthRlpRecipe(PythonRecipe):
    version = '0.2.2'
    url = 'https://github.com/ethereum/eth-account/archive/v{version}.tar.gz'
    depends = [('python2', 'python3crystax'), 'setuptools']
    patches = ['disable-setuptools-markdown.patch']


recipe = EthRlpRecipe()
