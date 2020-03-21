import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
# default pyethapp keystore path
KEYSTORE_DIR_SUFFIX = ".config/pyethapp/keystore/"
ENV_PATH = os.path.join(BASE_DIR, 'env.env')
NO_ACCOUNT_SELECTED_STRING = 'No account selected'
