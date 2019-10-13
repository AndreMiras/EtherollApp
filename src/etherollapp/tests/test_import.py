import unittest


class ModulesImportTestCase(unittest.TestCase):
    """Simple test cases, verifying core modules were installed properly."""

    def test_hashlib_sha3(self):
        import hashlib
        self.assertIsNotNone(hashlib.sha3_512())

    def test_pyetheroll(self):
        from pyetheroll.etheroll import Etheroll
        self.assertTrue(hasattr(Etheroll, 'player_roll_dice'))


if __name__ == '__main__':
    unittest.main()
