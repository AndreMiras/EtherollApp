from datetime import datetime


class PyEtherollTestUtils:
    """
    Copy of some helper members from:
    https://github.com/AndreMiras/pyetheroll/blob/20181031/
    tests/test_etheroll.py#L18
    """
    bet_logs = [
        {
            'bet_id': (
                '15e007148ec621d996c886de0f2b88a0'
                '3af083aa819e851a51133dc17b6e0e5b'),
            'bet_value_ether': 0.45,
            'datetime': datetime(2018, 4, 7, 0, 17, 6),
            'profit_value_ether': 44.1,
            'reward_value_ether': 44.55,
            'roll_under': 2,
            'timestamp': '0x5ac80e02',
            'transaction_hash': (
                '0xf363906a9278c4dd300c50a3c9a2790'
                '0bb85df60596c49f7833c232f2944d1cb')
        },
        {
            'bet_id': (
                '14bae6b4711bdc5e3db19983307a9208'
                '1e2e7c1d45161117bdf7b8b509d1abbe'),
            'bet_value_ether': 0.45,
            'datetime': datetime(2018, 4, 7, 0, 20, 14),
            'profit_value_ether': 6.97,
            'reward_value_ether': 7.42,
            'roll_under': 7,
            'timestamp': '0x5ac80ebe',
            'transaction_hash': (
                '0x0df8789552248edf1dd9d06a7a90726'
                'f1bc83a9c39f315b04efb6128f0d02146')
        },
        {
            # that one would not have been yet resolved (no `LogResult`)
            'bet_id': (
                'c2997a1bad35841b2c30ca95eea9cb08'
                'c7b101bc14d5aa8b1b8a0facea793e05'),
            'bet_value_ether': 0.5,
            'datetime': datetime(2018, 4, 7, 0, 23, 46),
            'profit_value_ether': 3.31,
            'reward_value_ether': 3.81,
            'roll_under': 14,
            'timestamp': '0x5ac80f92',
            'transaction_hash': (
                '0x0440f1013a5eafd88f16be6b5612b6e'
                '051a4eb1b0b91a160c680295e7fab5bfe')
        }
    ]

    bet_results_logs = [
        {
            'bet_id': (
                '15e007148ec621d996c886de0f2b88a0'
                '3af083aa819e851a51133dc17b6e0e5b'),
            'bet_value_ether': 0.45,
            'datetime': datetime(2018, 4, 7, 0, 17, 55),
            'dice_result': 86,
            'roll_under': 2,
            'timestamp': '0x5ac80e33',
            'transaction_hash': (
                '0x3505de688dc20748eb5f6b3efd6e6d3'
                '66ea7f0737b4ab17035c6b60ab4329f2a')
        },
        {
            'bet_id': (
                '14bae6b4711bdc5e3db19983307a9208'
                '1e2e7c1d45161117bdf7b8b509d1abbe'),
            'bet_value_ether': 0.45,
            'datetime': datetime(2018, 4, 7, 0, 20, 54),
            'dice_result': 51,
            'roll_under': 7,
            'timestamp': '0x5ac80ee6',
            'transaction_hash': (
                '0x42df3e3136957bcc64226206ed177d5'
                '7ac9c31e116290c8778c97474226d3092')
        },
    ]
