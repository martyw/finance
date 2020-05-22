"""
Implementation of a mean-reverting strategy
based on the Strategy class
"""
import logging
from typing import List, Dict

import pandas as pd

from constants import DEFAULT_QUANTITY, INCREMENT, DUMMY_CPTY, OUR_CPTY
from market.market_data import MarketData
from market.quote import Quote, asdict
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
