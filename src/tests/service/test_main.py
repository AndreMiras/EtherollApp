import unittest
from unittest import mock

from kivy.app import App

from service.main import ServiceApp


class TestServiceApp(unittest.TestCase):

    @staticmethod
    def patch_platform():
        return mock.patch('service.main.platform', 'android')

    @staticmethod
    def patch_jnius(m_jnius=mock.MagicMock()):
        return mock.patch.dict('sys.modules', jnius=m_jnius)

    def test_init(self):
        """
        Checks the ServiceApp initializes correctly.
        Checks the singleton via App.get_running_app() is available.
        """
        App._running_app = None
        assert App.get_running_app() is None
        app_name = 'etheroll'
        app = ServiceApp(app_name)
        assert App.get_running_app() == app
        assert app.name == 'etheroll'

    def test_get_user_data_dir(self):
        """
        Verifies `_get_user_data_dir()` returns the app directory.
        """
        app_name = 'etheroll'
        app = ServiceApp(app_name)
        assert app._get_user_data_dir().endswith('.config/etheroll')

    def test_get_user_data_dir_android(self):
        """
        On Android, pyjnius is used to call getAbsolutePath().
        """
        app_name = 'etheroll'
        app = ServiceApp(app_name)
        m_jnius = mock.MagicMock()
        with self.patch_platform(), self.patch_jnius(m_jnius):
            assert app._get_user_data_dir()
        assert m_jnius.cast().getAbsolutePath.call_args_list == [mock.call()]


if __name__ == '__main__':
    unittest.main()
