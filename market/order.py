""" order base class
"""
import itertools
import logging
from datetime import datetime
from market.side import Side
from typing import Dict


class Order:
    """
    Orders represent the core piece of the exchange. Every bid/ask is an Order.
    """
    newid = itertools.count(1)

    def __init__(self, quote: Dict):
        """ check if quote has required properties and assign them
        """
        if 'trade_id' in quote:
            self.dealer_or_broker_id = quote['trade_id']
        else:
            self.dealer_or_broker_id = quote['dealer_or_broker_id']

        self.side = quote['side']
        self.quantity = quote['quantity']
        self.order_id = next(Order.newid)

        logging.debug("*** Order: broker %s, side %s, qty %s, id %s, limit %s",
                      self.dealer_or_broker_id, self.side, self.quantity,
                      self.order_id, self.limit)

        if "symbol" in quote:
            self._symbol = quote["symbol"]
        else:
            self._symbol = None

        if "timestamp" in quote:
            self.timestamp = quote["timestamp"]
        else:
            self.timestamp = datetime.utcnow()

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value: datetime):
        self._timestamp = value

    @property
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, value: str):
        self._symbol = value

    def __getitem__(self, item):
        """for quering properties in dict style"""
        items = {'order_id': self.order_id,
                 'quantity': self.quantity,
                 'side': str(self.side),
                 'dealer_or_broker': self.dealer_or_broker_id,
                 'trade_id': self.dealer_or_broker_id}

        return items[item]

    @property
    def dealer_or_broker_id(self):
        """dealer broker"""
        return self._dealer_or_broker_id

    @dealer_or_broker_id.setter
    def dealer_or_broker_id(self, cpty: str):
        """dealer broker"""
        self._dealer_or_broker_id = cpty

    @property
    def quantity(self):
        """quantity"""
        return self._quantity

    @quantity.setter
    def quantity(self, qty: int):
        """quantity"""
        qty = int(qty)
        assert qty >= 0
        self._quantity = qty

    @property
    def side(self):
        """bid or ask"""
        return self._side

    @side.setter
    def side(self, ask_bid: str):
        """bid or ask"""
        self._side = Side[ask_bid.upper()]

    @property
    def limit(self):
        """to be implemented by derived class"""
        raise NotImplementedError

    def matches(self, potential_match):
        """calculate if incoming order matches this one"""
        if self._side == Side.BID:
            retval = self.limit > potential_match.limit
        else:
            retval = self.limit < potential_match.limit

        return retval

    def __eq__(self, other):
        """when order ids match orders are equal"""
        return self.order_id == other.order_id

    def __ne__(self, other):
        """not __eq__"""
        return not self.__eq__(other)

    def __lt__(self, other):
        """
            | dealer_or_broker | Side     | Qty | Price |
            | A      | Buy/bid  | 100 | 10.4  |
            | B      | Buy/bid  | 200 | 10.3  |
            | C      | Sell/ask | 100 | 10.7  |
            | D      | Sell/ask | 200 | 10.8  |
        """
        if self._side == Side.BID:
            if self.limit == other.limit:
                retval = self.order_id < other.order_id
            else:
                retval = self.limit > other.limit
        else:
            if self.limit == other.limit:
                retval = self.order_id < other.order_id
            else:
                retval = self.limit < other.limit

        logging.debug('%s __lt__ %s: %s', self, other, retval)

        return retval

    def __le__(self, other):
        """less or equal"""
        return NotImplemented

    def __gt__(self, other):
        """not __lt__"""
        retval = not self.__lt__(other)
        logging.debug('%s __gt__ %s: %s', self, other, retval)
        return retval

    def __ge__(self, other):
        """greater or equal"""
        return NotImplemented
