"""
limit order, only executes of counter trade matches on level
"""
from market.order import Order


class LimitOrder(Order):
    """Limit order"""
    def __init__(self, quote):
        self._limit = None
        assert 'price' in quote
        self.limit = quote['price']
        super().__init__(quote)

    @property
    def limit(self):
        """limit"""
        return self._limit

    @limit.setter
    def limit(self, price: float):
        """limit"""
        self._limit = float(price)

    def __getitem__(self, item: str):
        """for quering properties in dict style"""
        if item == 'type':
            return 'limit'

        if item in ('price', 'limit'):
            return self.limit

        return super().__getitem__(item)

    def __repr__(self):
        """for debugging and printing"""
        return "{}@{}/{} - {}".format(self.quantity, self.limit,
                                      self.dealer_or_broker_id, self.order_id)
