from unittest import mock

from etherollapp.etheroll.utils import get_etherscan_api_key


class TestUtils:
    def test_get_etherscan_api_key(self):
        """
        Verifies the key can be retrieved from either:
        1) environment
        2) file
        3) or fallbacks on default key
        """
        expected_key = "0102030405060708091011121314151617"
        # 1) environment
        with mock.patch.dict(
            "os.environ", {"ETHERSCAN_API_KEY": expected_key}
        ):
            actual_key = get_etherscan_api_key()
        assert actual_key == expected_key
        # 2) file
        read_data = '{ "key" : "%s" }' % (expected_key)
        api_key_path = "api_key.json"
        with mock.patch(
            "builtins.open", mock.mock_open(read_data=read_data)
        ) as m_open:
            actual_key = get_etherscan_api_key(api_key_path=api_key_path)
        assert expected_key == actual_key
        # verifies the file was read
        assert m_open.call_args_list == [mock.call(api_key_path, mode="r")]
        # 3) or fallbacks on default key
        with mock.patch("builtins.open") as m_open, mock.patch(
            "etherollapp.etheroll.utils.logger"
        ) as m_logger:
            m_open.side_effect = FileNotFoundError
            actual_key = get_etherscan_api_key(api_key_path)
        assert "YourApiKeyToken" == actual_key
        # verifies the fallback warning was logged
        assert m_logger.warning.call_args_list == [
            mock.call(
                "Cannot get Etherscan API key. "
                "File api_key.json not found, "
                "defaulting to YourApiKeyToken."
            )
        ]
