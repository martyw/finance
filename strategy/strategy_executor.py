import logging
from datetime import datetime
from typing import List
from typing import Dict

import pandas as pd

from market.market_data import MarketData
from position_keeping.position import Position
from position_keeping.trade import Trade
from orderbook.matching_engine import MatchingEngine
from constants import DEFAULT_SERVICE
from strategy.strategy import Strategy


class Executor:
    """
    This class executes a strategy by calling method market_data_tick
    The strategy has to be set by calling the setter
    """
    def __init__(self, symbol: str, data_source: str = DEFAULT_SERVICE):
        self.symbol = symbol
        self.market_data_source = data_source
        self._strategy = None
        self.matching_engine = MatchingEngine()
        self.positions = dict()
        self.current_prices = None
        self.pnl = pd.DataFrame(columns = ["Realized PnL", "Unrealized PnL"])

    @property
    def strategy(self):
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: Strategy):
        self._strategy = strategy

    def get_timestamp(self) -> datetime:
        return self.current_prices.get_timestamp(self.symbol)

    def get_trade_date(self) -> str:
        timestamp = self.get_timestamp()
        return timestamp.strftime("%Y-%m-%d")

    def update_filled_position(self, trades: List[Trade], close_price: float) \
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
