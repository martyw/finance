""" A container to store latest known prices for a list of symbols """
from market.tick_data import TickData
from datetime import datetime
import unittest
import logging


class MarketData:
    def __init__(self):
        self.__recent_ticks__ = dict()

    def add_last_price(self, time, symbol, price, volume):
        logging.debug("add last {0}, {1} - {2}/{3}".format(time, symbol,
                                                           price, volume))
        tick_data = TickData(symbol, price, volume, time)
        self.__recent_ticks__[symbol] = tick_data

    def add_open_price(self, time, symbol, price):
        logging.debug("add open {0}, {1} - {2}".format(time, symbol, price))
        tick_data = self.get_existing_tick_data(symbol)
        tick_data.open_price = price

    def get_existing_tick_data(self, symbol) -> TickData:
        if symbol not in self.__recent_ticks__:
            self.__recent_ticks__[symbol] = TickData(symbol)

        return self.__recent_ticks__[symbol]

    def get_last_price(self, symbol) -> float:
        return self.__recent_ticks__[symbol].last_price

    def get_open_price(self, symbol) -> float:
        return self.__recent_ticks__[symbol].open_price

    def get_timestamp(self, symbol) -> datetime:
        return self.__recent_ticks__[symbol].timestamp

    def __str__(self):
        return str(self.__recent_ticks__)


class TestMarketData(unittest.TestCase):
    """
    Test Curve class
    """
    def setUp(self) -> None:
        self.md = MarketData()
        self.timestamp = datetime.now()
        self.last = 3.1415926

    def test_last(self):
        """test last, timestamp"""
        t = self.md.get_existing_tick_data("TEST")
        self.assertEqual(0.0, t.last_price)

        self.md.add_last_price(self.timestamp, "TEST", self.last, 123456)
        t = self.md.get_existing_tick_data("TEST")
        self.assertEqual(self.last, t.last_price)
        self.assertEqual(self.timestamp, t.timestamp)

    def test_open(self):
        """test open price"""
        self.md.add_open_price(self.timestamp, "TEST", self.last)
        open = self.md.get_open_price("TEST")
        self.assertEqual(self.last, open)


if __name__ == '__main__':
    unittest.main()
