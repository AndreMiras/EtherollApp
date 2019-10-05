import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
# default pyethapp keystore path
KEYSTORE_DIR_SUFFIX = ".config/pyethapp/keystore/"
API_KEY_PATH = os.path.join(BASE_DIR, 'api_key.json')
NO_ACCOUNT_SELECTED_STRING = 'No account selected'
