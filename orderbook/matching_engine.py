""" order book on a security

internal the order book is set up as two sorted lists of orders, one for bids
and one for asks.

key logic is in method match_order, an incoming order is matched against the
orders in the relevant list. if there is a remaining quantity after a partial
fill a replacement order is added to the book. trades are returned
"""
import logging
from typing import Dict
from sortedcontainers import SortedList
from market.order_factory import create_order
from market.side import Side
from position_keeping.trade import Trade


class MatchingEngine:
    """ implements an order book on one security
    """
    def __init__(self):
        """ initialize
        """
        self.tape = []
        self.bids = SortedList()
        self.asks = SortedList()

    def match_order(self, quote: Dict):
        """ process order given in argument quote
        """
        order = create_order(quote)

        logging.debug('before processing asks are %s', self.asks)
        logging.debug('before processing bids are %s', self.bids)

        trades = []
        orders = self.asks if order.side == Side.BID else self.bids

        while orders and order.quantity > 0:
            if order.matches(orders[0]):
                trade = Trade(order, orders[0])
                order.quantity -= trade.quantity
                orders[0].quantity -= trade.quantity

                self.tape.append(trade)
                trades.append(trade)

                if not orders[0].quantity:
                    orders.pop(0)
            else:
                break

            logging.debug('orders: %s, trades: %s, remaining quantity: %s',
                          orders, trades, order.quantity)

        # If not fully filled update the book with a new order
        # with remaining quantity
        if order.quantity > 0:
            orders = self.asks if order.side == Side.ASK else self.bids
            orders.add(order)
            order_in_book = order
        else:
            order_in_book = None

        logging.debug('after processing asks are %s', self.asks)
        logging.debug('after processing bids are %s', self.bids)
        logging.debug('after processing trades are %s', trades)

        return trades, order_in_book

    def get_volume_at_price(self, side: str, price: float) -> int:
        """ get the volume available in the orderbook
        """
        bid_or_ask = Side[side.upper()]
        volume = 0

        orders = self.bids if bid_or_ask == Side.BID else self.asks

        for i in orders:
            if i.limit == price:
                volume += i.quantity

        return volume

    def get_best_bid(self) -> float:
        """ get best bid from orderbook
        """
        return self.bids[0].limit

    def get_worst_bid(self) -> float:
        """ get worst bid from orderbook
        """
        return self.bids[-1].limit

    def get_best_ask(self) -> float:
        """ get best ask from orderbook
        """
        return self.asks[0].limit

    def get_worst_ask(self) -> float:
        """ get worst ask from orderbook
        """
        return self.asks[-1].limit

    def tape_dump(self,
                  filename: str,
                  filemode: str = 'w',
                  tapemode: str = None):
        """ write trades to file in arg filename
        """
        with open(filename, filemode) as dumpfile:
            template = 'Price: %s, Quantity: %s\n'
            for i in self.tape:
                dumpfile.write(template % (i['price'], i['quantity']))

        if tapemode == 'wipe':
            self.tape = []

    def __str__(self):
        """ orderbook representation
        """
        ret = "***Bids***\n"
        for value in self.bids:
            ret += str(value)

        ret += "\n***Asks***\n"
        for value in self.asks:
            ret += str(value)

        ret += "\n***Trades***\n"
        # print first 10 trades
        for i in range(10):
            try:
                ret += str(self.tape[i]) + '\n'
            except IndexError:
                break

        return ret + '\n'
