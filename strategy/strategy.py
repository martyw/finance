""" Base strategy for implementation """
from position_keeping.long_short import LongShort


class Strategy:
    def __init__(self, symbol: str, test_mode: bool = False):
        self.symbol = symbol
        self._long_short = LongShort.NO_POSITION
        self.test_mode = test_mode

    def market_data_tick(self, market_data):
        raise NotImplementedError

    @property
    def long_short(self):
        return self._long_short

    @long_short.setter
    def long_short(self, long_or_short: LongShort):
        self._long_short = long_or_short
