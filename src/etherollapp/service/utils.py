import json

from kivy.utils import platform


def start_roll_polling_service(arguments=None):
    """
    Starts the roll polling service.
    If the service is already running, it won't be started twice.
    """
    if platform != 'android':
        return
    from jnius import autoclass
    package_name = 'etheroll'
    package_domain = 'com.github.andremiras'
    service_name = 'service'.title()
    service_class = f'{package_domain}.{package_name}.Service{service_name}'
    service = autoclass(service_class)
    mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
    argument = json.dumps(arguments)
    service.start(mActivity, argument)
