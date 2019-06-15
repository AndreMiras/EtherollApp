import binascii
import unittest
from unittest import mock

from kivy.app import App
from pyetheroll.constants import ChainID

from service.main import MonitorRollsService, ServiceApp


def patch_platform():
    return mock.patch('service.main.platform', 'android')


def patch_jnius(m_jnius=mock.MagicMock()):
    return mock.patch.dict('sys.modules', jnius=m_jnius)


class TestServiceApp(unittest.TestCase):
    """
    Unit tests ServiceApp methods.
    """

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
        with patch_platform(), patch_jnius(m_jnius):
            assert app._get_user_data_dir()
        assert m_jnius.cast().getAbsolutePath.call_args_list == [mock.call()]


class TestMonitorRollsService(unittest.TestCase):
    """
    Unit tests MonitorRollsService methods.
    """

    def patch_get_merged_logs(m_get):
        return mock.patch('service.main.Etheroll.get_merged_logs')

    def test_init(self):
        """
        Initializes MonitorRollsService with/without osc server port param.
        """
        service = MonitorRollsService()
        assert service is not None
        assert service.osc_app_client is None
        osc_server_port = 1234
        service = MonitorRollsService(osc_server_port)
        assert service.osc_app_client is not None

    def test_run(self):
        """
        Verifies the `run()` method exits calling `set_auto_restart_service()`.
        """
        service = MonitorRollsService()
        with mock.patch('service.main.NO_ROLL_ACTIVITY_PERDIOD_SECONDS', 0), \
                mock.patch.object(
                    MonitorRollsService,
                    'set_auto_restart_service') as m_set_auto_restart_service:
            service.run()
        assert m_set_auto_restart_service.call_args_list == [mock.call(False)]

    def test_account_utils(self):
        service = MonitorRollsService()
        assert service.account_utils is not None

    def test_set_auto_restart_service(self):
        """
        On Android it should be calling `setAutoRestartService()`. On other OS
        this is a NOP.
        """
        service = MonitorRollsService()
        m_jnius = mock.MagicMock()
        with patch_jnius(m_jnius):
            service.set_auto_restart_service()
        assert m_jnius.autoclass.called is False
        with patch_platform(), patch_jnius(m_jnius):
            service.set_auto_restart_service()
        assert m_jnius.autoclass.called is True
        mservice = m_jnius.autoclass().mService
        assert mservice.setAutoRestartService.call_args_list == [
            mock.call(True)
        ]

    def test_pyetheroll(self):
        """
        Checks that pyetheroll is cached.
        The cached value should be updated on (testnet/mainnet) network change.
        """
        service = MonitorRollsService()
        assert service._pyetheroll is None
        assert service.pyetheroll is not None
        assert service._pyetheroll is not None
        pyetheroll = service.pyetheroll
        assert pyetheroll == service.pyetheroll
        assert pyetheroll.chain_id == ChainID.MAINNET
        # the cached pyetheroll object is invalidated if the network changes
        with mock.patch(
                'service.main.Settings.get_stored_network'
                ) as m_get_stored_network:
            m_get_stored_network.return_value = ChainID.ROPSTEN
            assert service.pyetheroll.chain_id == ChainID.ROPSTEN
            assert service.pyetheroll != pyetheroll

    def test_get_running_app(self):
        app = MonitorRollsService.get_running_app()
        assert isinstance(app, ServiceApp)
        assert app.name == 'etheroll'

    def test_pull_account_rolls(self):
        """
        Makes sure the merged logs are fetched and cached.
        Also checks were're notifying on merged logs changes.
        """
        service = MonitorRollsService()
        address = '46044beAa1E985C67767E04dE58181de5DAAA00F'
        m_account = mock.MagicMock()
        m_account.address = binascii.unhexlify(address)
        # beforehand the `MonitorRollsService.merged_logs` is not yet cached
        assert service.merged_logs == {}
        assert service.last_roll_activity is None
        merged_logs = []
        with self.patch_get_merged_logs() as m_get_merged_logs:
            m_get_merged_logs.return_value = merged_logs
            service.pull_account_rolls(m_account)
        # then the `merged_logs` for this address should be cached
        assert service.merged_logs == {f'0x{address.lower()}': merged_logs}
        assert service.last_roll_activity is None
        # if the `merged_logs` differs, we consider it was a roll activity
        merged_logs = ['something else']
        with self.patch_get_merged_logs() as m_get_merged_logs, \
                mock.patch.object(
                    MonitorRollsService, 'do_notify') as m_do_notify:
            m_get_merged_logs.return_value = merged_logs
            service.pull_account_rolls(m_account)
        assert m_do_notify.call_args_list == [mock.call(merged_logs)]

    def test_pull_accounts_rolls(self):
        """
        Checks `pull_accounts_rolls()` iterates over the accounts and call
        `pull_account_rolls()` for each.
        """
        service = MonitorRollsService()
        address = '46044beAa1E985C67767E04dE58181de5DAAA00F'
        m_account = mock.MagicMock()
        m_account.address = binascii.unhexlify(address)
        with mock.patch(
                'service.main.AccountUtils.get_account_list'
                ) as m_get_account_list, \
                mock.patch.object(
                    MonitorRollsService, 'pull_account_rolls'
                ) as m_pull_account_rolls:
            m_get_account_list.return_value = [m_account]
            service.pull_accounts_rolls()
        assert m_pull_account_rolls.call_args_list == [
            mock.call(m_account),
        ]

    @unittest.skip("Not implemented")
    def test_do_notify(self):
        """
        Not yet implemented.
        """
        raise NotImplementedError


if __name__ == '__main__':
    unittest.main()
