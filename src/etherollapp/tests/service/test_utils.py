import unittest
from unittest import mock

from etherollapp.service import utils


class TestUtils(unittest.TestCase):

    @staticmethod
    def patch_platform():
        return mock.patch('etherollapp.service.utils.platform', 'android')

    @staticmethod
    def patch_jnius(m_jnius=mock.MagicMock()):
        return mock.patch.dict('sys.modules', jnius=m_jnius)

    def test_start_roll_polling_service(self):
        """
        Call `start_roll_polling_service()` with and without args.
        Verifies the PythonActivity is being created and started.
        """
        # test without args
        m_jnius = mock.MagicMock()
        with self.patch_platform(), self.patch_jnius(m_jnius):
            utils.start_roll_polling_service()
        assert m_jnius.autoclass().start.call_args_list == [
            mock.call(m_jnius.autoclass().mActivity, 'null')
        ]
        # test with args
        m_jnius = mock.MagicMock()
        arguments = {'foo': 'bar', 'foobar': True}
        with self.patch_platform(), self.patch_jnius(m_jnius):
            utils.start_roll_polling_service(arguments)
        assert m_jnius.autoclass.call_args_list == [
            mock.call('com.github.andremiras.etheroll.ServiceService'),
            mock.call('org.kivy.android.PythonActivity'),
        ]
        assert m_jnius.autoclass().start.call_args_list == [
            mock.call(
                m_jnius.autoclass().mActivity,
                '{"foo": "bar", "foobar": true}')
        ]


if __name__ == '__main__':
    unittest.main()
