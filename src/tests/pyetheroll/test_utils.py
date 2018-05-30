import unittest

from pyetheroll.utils import EtherollUtils


class TestEtherollUtils(unittest.TestCase):

    def test_compute_profit(self):
        bet_size = 0.10
        chances_win = 34
        payout = EtherollUtils.compute_profit(bet_size, chances_win)
        self.assertEqual(payout, 0.19)
        bet_size = 0.10
        # chances of winning must be less than 100%
        chances_win = 100
        payout = EtherollUtils.compute_profit(bet_size, chances_win)
        self.assertEqual(payout, None)
