import unittest
from datetime import datetime

from market.market_data import MarketData


class TestMarketData(unittest.TestCase):
    """
    Test Curve class
    """
    def setUp(self) -> None:
        self.market_data = MarketData()
        self.symbol = "TEST"
        self.timestamp = datetime.now()
        self.last = 3.1415926
        self.open = 2.71828
        self.volume = 123456

    def test_data(self):
        """test last, timestamp"""
        last_tick = self.market_data.get_existing_tick_data(self.symbol)
        self.assertEqual(0.0, last_tick.last_price)
        self.assertEqual(0.0, last_tick.open_price)
        self.assertEqual(0, last_tick.total_volume)

        self.market_data.add_last_price(self.timestamp,
                                        self.symbol,
                                        self.last, 123456)
        last_tick = self.market_data.get_existing_tick_data(self.symbol)
        self.assertEqual(self.last, last_tick.last_price)
        self.assertEqual(0.0, last_tick.open_price)
        self.assertEqual(self.timestamp, last_tick.timestamp)

        self.market_data.add_open_price(self.timestamp, self.symbol, self.open)

        open_price = self.market_data.get_open_price(self.symbol)
        self.assertEqual(open_price, self.open)
        last = self.market_data.get_last_price(self.symbol)
        self.assertEqual(last, self.last)
        time = self.market_data.get_timestamp(self.symbol)
        self.assertEqual(time, self.timestamp)
