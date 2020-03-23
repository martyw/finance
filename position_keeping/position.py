"""Position"""
from typing import List
from position_keeping.trade import Trade
from position_keeping.long_short import LongShort
from constants import OUR_CPTY


class Position:
    def __init__(self):
        self.symbol = None
        self.buys = 0
        self.sells = 0
        self.net = 0.0
        self.realized_pnl = 0.0
        self.unrealized_pnl = 0.0
        self.position_value = 0.0
        self.long_short = LongShort.NO_POSITION

    def update(self, trades: List[Trade], close: float):
        self.append(trades)
        self.update_unrealized_pnl(close)

    def append(self, trades: List[Trade]):
        for trade in trades:
            if trade["buyer"] == OUR_CPTY:
                self.buys += trade.quantity
                self.position_value -= trade.quantity * trade.price
            else:
                self.sells += trade.quantity
                self.position_value += trade.quantity * trade.price

        self.net = self.buys - self.sells

        if self.net > 0:
            self.long_short = LongShort.LONG
        elif self.net < 0:
            self.long_short = LongShort.SHORT
        else:
            self.long_short = LongShort.NO_POSITION
            self.realized_pnl = self.position_value

    def update_unrealized_pnl(self, price: float) -> float:
        if self.net == 0:
            self.unrealized_pnl = 0
        else:
            self.unrealized_pnl = price * self.net + self.position_value

        return self.unrealized_pnl

    def __str__(self):
        return "Net: {}, Value: {}, UPnL: {}, RPnL: {}".\
            format(self.net,
                   self.position_value,
                   self.unrealized_pnl,
                   self.realized_pnl)
