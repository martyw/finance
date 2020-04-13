""" A container to store latest known prices for a list of symbols """
import logging
import unittest
from datetime import datetime

from market.tick_data import TickData


class MarketData:
    def __init__(self):
        self.__recent_ticks__ = dict()

    def add_last_price(self,
                       time: datetime,
                       symbol: str,
                       price: float,
                       volume: int):
        logging.debug("add last {0}, {1} - {2}/{3}".format(time, symbol,
                                                           price, volume))
        tick_data = TickData(symbol=symbol, last_price=price,
                             total_volume=volume, timestamp=time)
        self.__recent_ticks__[symbol] = tick_data

    def add_open_price(self,
                       time: datetime,
                       symbol: str,
                       price: float):
        logging.debug("add open {0}, {1} - {2}".format(time, symbol, price))
        tick_data = self.get_existing_tick_data(symbol)
        tick_data.open_price = price
        self.__recent_ticks__[symbol] = tick_data

    def get_existing_tick_data(self, symbol: str) -> TickData:
        if symbol not in self.__recent_ticks__:
            self.__recent_ticks__[symbol] = TickData(symbol=symbol)

        return self.__recent_ticks__[symbol]

    def get_last_price(self, symbol: str) -> float:
        return self.__recent_ticks__[symbol].last_price

    def get_open_price(self, symbol: str) -> float:
        return self.__recent_ticks__[symbol].open_price

    def get_timestamp(self, symbol: str) -> datetime:
        return self.__recent_ticks__[symbol].timestamp

    def __str__(self):
        return str(self.__recent_ticks__)


class TestMarketData(unittest.TestCase):
    """
    Test Curve class
    """
    def setUp(self) -> None:
        self.md = MarketData()
        self.symbol = "TEST"
        self.timestamp = datetime.now()
        self.last = 3.1415926
        self.open = 2.71828
        self.volume = 123456

    def test_data(self):
        """test last, timestamp"""
        last_tick = self.md.get_existing_tick_data(self.symbol)
        self.assertEqual(0.0, last_tick.last_price)
        self.assertEqual(0.0, last_tick.open_price)
        self.assertEqual(0, last_tick.total_volume)

        self.md.add_last_price(self.timestamp, self.symbol, self.last, 123456)
        last_tick = self.md.get_existing_tick_data(self.symbol)
        self.assertEqual(self.last, last_tick.last_price)
        self.assertEqual(0.0, last_tick.open_price)
        self.assertEqual(self.timestamp, last_tick.timestamp)

        self.md.add_open_price(self.timestamp, self.symbol, self.open)

        open = self.md.get_open_price(self.symbol)
        self.assertEqual(open, self.open)
        last = self.md.get_last_price(self.symbol)
        self.assertEqual(last, self.last)
        time = self.md.get_timestamp(self.symbol)
        self.assertEqual(time, self.timestamp)


if __name__ == '__main__':
    unittest.main()
