"""
Implementation of a mean-reverting strategy
based on the Strategy class
"""
import logging
import unittest
from datetime import datetime
from typing import List, Dict

import pandas as pd

from constants import DEFAULT_QUANTITY, INCREMENT, DUMMY_CPTY, OUR_CPTY
from market.market_data import MarketData
from market.quote import Quote, asdict
from market.tick_data import TickData
from position_keeping.long_short import LongShort
from strategy.strategy import Strategy


class MeanRevertingStrategy(Strategy):
    def __init__(self,
                 symbol: str,
                 test_mode: bool = False,
                 lookback_intervals: int = 20,
                 buy_threshold: float = -1.5,
                 sell_threshold: float = 1.5):

        super().__init__(symbol, test_mode)
        self.lookback_intervals = lookback_intervals
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        self.prices = pd.DataFrame()

    def market_data_tick(self, market_data: MarketData):
        self.store_prices(market_data)
        orders = []

        if len(self.prices) >= self.lookback_intervals:
            signal_value = self.calculate_z_score()

            if signal_value <= self.buy_threshold:
                logging.debug("buy signal")
                orders = self.on_buy_signal()
            elif signal_value > self.sell_threshold:
                logging.debug("sell signal")
                orders = self.on_sell_signal()
            else:
                pass
        return orders

    def on_buy_signal(self) -> List[Dict]:
        logging.debug("Long or short : {}".format(self.long_short))
        orders = []
        if self.long_short in (LongShort.SHORT, LongShort.NO_POSITION):
            last_price = self.prices.iloc[-1]["close"]
            if self.test_mode:
                # make sure order gets filled by adding a counter order
                # to the order book if in test mode
                quote = Quote(type="limit",
                              dealer_or_broker_id=DUMMY_CPTY,
                              symbol=self.symbol,
                              side="ask",
                              quantity=DEFAULT_QUANTITY,
                              price=last_price-INCREMENT)
                orders.append(asdict(quote))

            quote = Quote(type="limit",
                          dealer_or_broker_id=OUR_CPTY,
                          symbol=self.symbol,
                          side="bid",
                          quantity=DEFAULT_QUANTITY,
                          price=last_price)
            orders.append(asdict(quote))
        return orders

    def on_sell_signal(self) -> List[Dict]:
        logging.debug("Long or short : {}".format(self.long_short))
        orders = []
        if self.long_short in (LongShort.LONG, LongShort.NO_POSITION):
            last_price = self.prices.iloc[-1]["close"]
            logging.debug(self.prices)
            if self.test_mode:
                # make sure order gets filled by adding a counter order
                # to the order book if in test mode
                quote = Quote(type="limit",
                              dealer_or_broker_id=DUMMY_CPTY,
                              symbol=self.symbol,
                              side="bid",
                              quantity=DEFAULT_QUANTITY,
                              price=last_price + INCREMENT)
                orders.append(asdict(quote))

            quote = Quote(type="limit",
                          dealer_or_broker_id=OUR_CPTY,
                          symbol=self.symbol,
                          side="ask",
                          quantity=DEFAULT_QUANTITY,
                          price=last_price)
            orders.append(asdict(quote))
        return orders

    def store_prices(self, market_data: MarketData):
        timestamp = market_data.get_timestamp(self.symbol)
        self.prices.loc[timestamp, "close"] = \
            market_data.get_last_price(self.symbol)
        self.prices.loc[timestamp, "open"] = \
            market_data.get_open_price(self.symbol)

    def calculate_z_score(self) -> float:
        self.prices = self.prices[-self.lookback_intervals:]
        returns = self.prices["close"].pct_change().dropna()
        z_score = ((returns-returns.mean())/returns.std())[-1]
        return z_score


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
