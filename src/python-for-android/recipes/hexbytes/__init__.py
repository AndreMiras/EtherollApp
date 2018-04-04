from pythonforandroid.recipe import PythonRecipe


class HexbytesRecipe(PythonRecipe):
    version = '0.1.0'
    url = 'https://github.com/carver/hexbytes/archive/v{version}.tar.gz'
    depends = [('python2', 'python3crystax'), 'setuptools']
    patches = ['disable-setuptools-markdown.patch']


recipe = HexbytesRecipe()
