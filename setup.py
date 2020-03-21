import os

from setuptools import find_namespace_packages, setup

from src.etherollapp import version


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


# exposing the params so it can be imported
setup_params = {
    'name': 'EtherollApp',
    'version': version.__version__,
    'description': (
        'Provably fair dice game running on the Ethereum blockchain'),
    'long_description': read('README.md'),
    'long_description_content_type': 'text/markdown',
    'author': 'Andre Miras',
    'url': 'https://github.com/AndreMiras/EtherollApp',
    'packages': find_namespace_packages(
        where='src',
        exclude=(
            'distutils',
            'python-for-android',
            'python-for-android.*',
        ),
    ),
    'package_data': {'': ('*.kv', '*.md')},
    'package_dir': {'': 'src'},
    'entry_points': {
        'console_scripts': (
            'etherollapp=etherollapp.etheroll.controller:main',
        ),
    },
    'python_requires': '>=3',
    'install_requires': (
        'eth-account<=0.4.0',
        'eth-utils',
        'kivy-garden.kivymd',
        'layoutmargin',
        'oscpy',
        'pyetheroll>=20200320',
        'python-dotenv',
        'raven',
        'requests-cache',
        'web3',
    ),
}


def run_setup():
    setup(**setup_params)


# makes sure the setup doesn't run at import time
if __name__ == '__main__':
    run_setup()
