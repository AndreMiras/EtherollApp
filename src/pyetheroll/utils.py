from pyetheroll.constants import ROUND_DIGITS


class EtherollUtils:

    @staticmethod
    def compute_profit(bet_size, chances_win):
        """
        Helper method to compute profit given a bet_size and chances_win.
        """
        if chances_win <= 0 or chances_win >= 100:
            return
        house_edge = 1.0 / 100
        chances_loss = 100 - chances_win
        payout = ((chances_loss / chances_win) * bet_size) + bet_size
        payout *= (1 - house_edge)
        profit = payout - bet_size
        profit = round(profit, ROUND_DIGITS)
        return profit
