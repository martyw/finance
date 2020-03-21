"""
test a strategy with market data from yahoo
keep track of PnL over time
"""
import logging
from datetime import datetime, timedelta
from typing import List
from typing import Dict

import pandas as pd

from strategy.mean_reverting import MeanRevertingStrategy
from market_data_source import MarketDataSource
from market.market_data import MarketData
from position_keeping.position import Position
from position_keeping.trade import Trade
from orderbook.matching_engine import MatchingEngine
from constants import DEFAULT_SERVICE, TEST_MODE


class BackTester:
    def __init__(self,
                 symbol: str,
                 start_date: datetime,
                 end_date: datetime,
                 data_source: str = DEFAULT_SERVICE):

        self.symbol = symbol
        self.market_data_source = data_source
        self.start_date = start_date
        self.end_date = end_date
        self.strategy = None
        self.matching_engine = MatchingEngine()
        self.positions = dict()
        self.current_prices = None
        self.pnl = pd.DataFrame(columns = ["Realized PnL", "Unrealized PnL"])

    def get_timestamp(self) -> datetime:
        return self.current_prices.get_timestamp(self.symbol)

    def get_trade_date(self) -> str:
        timestamp = self.get_timestamp()
        return timestamp.strftime("%Y-%m-%d")

    def update_filled_position(self, trades: List[Trade], close_price: float)\
            -> Position:
        position = self.get_position()
        position.update(trades, close_price)

        return position

    def update_pnl(self, position: Position):
        self.pnl.loc[self.get_timestamp()] = [position.realized_pnl,
                                              position.unrealized_pnl]
        logging.info("{}, {}".format(self.get_trade_date(), position))

    def get_position(self) -> Position:
        if self.symbol not in self.positions:
            position = Position()
            position.symbol = self.symbol
            self.positions[self.symbol] = position

        return self.positions[self.symbol]

    def send_order_to_market(self, orders: List[Dict]) -> List[Trade]:
        resulting_trades = []
        for order in orders:
            msg = "{} Received order: {} {}".format(self.get_trade_date(),
                                                    order["quantity"],
                                                    order["symbol"])
            logging.debug(msg)
            trades, _ = self.matching_engine.match_order(order)
            resulting_trades.extend(trades)

        return resulting_trades

    def market_data_tick(self, prices: MarketData):
        self.current_prices = prices

        orders = self.strategy.market_data_tick(prices)
        trades = self.send_order_to_market(orders)

        close_price = prices.get_last_price(self.symbol)
        position = self.update_filled_position(trades, close_price)

        self.update_pnl(position)
        self.strategy.long_short = position.long_short

    def start_back_test(self, test_mode: bool = False):
        self.strategy = MeanRevertingStrategy(self.symbol, test_mode)

        mds = MarketDataSource(self.symbol, self.market_data_source,
                               self.start_date, self.end_date)

        logging.info("Backtesting started...")
        for tick in mds.market_simulation():
            self.market_data_tick(tick)
        logging.info("Completed")


if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s:%(message)s',
                        level=logging.DEBUG)
    back_test = BackTester("AAPL",
                           datetime(2014, 1, 1),
                           datetime(2014, 12, 31))
    back_test.start_back_test(TEST_MODE)

    import matplotlib.pyplot as plt

    dates = [pd.to_datetime(x) for x in back_test.pnl.index.values.tolist()]
    plt.plot(dates, back_test.pnl["Realized PnL"])
    plt.plot(dates, back_test.pnl["Unrealized PnL"])
    plt.legend(list(back_test.pnl.columns) )
    plt.xlabel("time")
    plt.ylabel("Profit and Loss")
    plt.show()