from datetime import datetime
import unittest
from constants import OUR_CPTY
from market.tick_data import TickData
from market.market_data import MarketData
from strategy.mean_reverting import MeanRevertingStrategy


class TestMeanReverting(unittest.TestCase):
    def setUp(self):
        self.symbol = "AAPL"
        self.volume = 100
        self.prices = {}
        self.prices[datetime(2014, 1, 30)] = TickData(symbol=self.symbol, last_price=71.397141, open_price=71.791428)   # noqa
        self.prices[datetime(2014, 1, 31)] = TickData(symbol=self.symbol, last_price=71.514282, open_price=70.739998)   # noqa
        self.prices[datetime(2014, 2, 3)] = TickData(symbol=self.symbol, last_price=71.647141, open_price=71.801430)   # noqa
        self.prices[datetime(2014, 2, 4)] = TickData(symbol=self.symbol, last_price=72.684288, open_price=72.264282)   # noqa
        self.prices[datetime(2014, 2, 5)] = TickData(symbol=self.symbol, last_price=73.227142, open_price=72.365715)   # noqa
        self.prices[datetime(2014, 2, 6)] = TickData(symbol=self.symbol, last_price=73.215714, open_price=72.865715)   # noqa
        self.prices[datetime(2014, 2, 7)] = TickData(symbol=self.symbol, last_price=74.239998, open_price=74.482857)   # noqa
        self.prices[datetime(2014, 2, 10)] = TickData(symbol=self.symbol, last_price=75.570000, open_price=74.094284)   # noqa
        self.prices[datetime(2014, 2, 11)] = TickData(symbol=self.symbol, last_price=76.565712, open_price=75.801430)   # noqa
        self.prices[datetime(2014, 2, 12)] = TickData(symbol=self.symbol, last_price=76.559998, open_price=76.707146)   # noqa
        self.prices[datetime(2014, 2, 13)] = TickData(symbol=self.symbol, last_price=77.775711, open_price=76.379997)   # noqa
        self.prices[datetime(2014, 2, 14)] = TickData(symbol=self.symbol, last_price=77.712860, open_price=77.495712)   # noqa
        self.prices[datetime(2014, 2, 18)] = TickData(symbol=self.symbol, last_price=77.998573, open_price=78.000000)   # noqa
        self.prices[datetime(2014, 2, 19)] = TickData(symbol=self.symbol, last_price=76.767143, open_price=77.821426)   # noqa
        self.prices[datetime(2014, 2, 20)] = TickData(symbol=self.symbol, last_price=75.878571, open_price=76.141426)   # noqa
        self.prices[datetime(2014, 2, 21)] = TickData(symbol=self.symbol, last_price=75.035713, open_price=76.112854)   # noqa
        self.prices[datetime(2014, 2, 24)] = TickData(symbol=self.symbol, last_price=75.364288, open_price=74.735718)   # noqa
        self.prices[datetime(2014, 2, 25)] = TickData(symbol=self.symbol, last_price=74.580002, open_price=75.625717)   # noqa
        self.prices[datetime(2014, 2, 26)] = TickData(symbol=self.symbol, last_price=73.907143, open_price=74.801430)   # noqa
        self.prices[datetime(2014, 2, 27)] = TickData(symbol=self.symbol, last_price=75.381432, open_price=73.877144)   # noqa
        self.algo = MeanRevertingStrategy(self.symbol)

    def testReverting(self):
        self.assertEqual(self.symbol, "AAPL")
        time_stamp = None
        for time_stamp in self.prices:
            md = MarketData()
            md.add_last_price(time=time_stamp,
                              symbol=self.symbol,
                              price=self.prices[time_stamp].last_price,
                              volume=self.volume)
            md.add_open_price(time=time_stamp,
                              symbol=self.symbol,
                              price=self.prices[time_stamp].open_price)
            orders = self.algo.market_data_tick(md)
            if orders:
                break

        self.assertEqual(time_stamp, datetime(2014, 2, 27))

        our_quote = {"type": "limit",
                     "dealer_or_broker_id": OUR_CPTY,
                     "symbol": self.symbol,
                     "side": "ask",
                     "quantity": self.volume,
                     "price": 75.381432}
        self.assertEqual(orders, [our_quote])
