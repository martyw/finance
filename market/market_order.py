"""
Market order, executes always if liquidity is available
"""
from market.order import Order
from market.side import Side


class MarketOrder(Order):
    """market order, execute always"""
    def __getitem__(self, item):
        """for quering properties in dict style"""
        if item == 'type':
            retval = 'market'
        else:
            retval = super().__getitem__(item)

        return retval

    def __repr__(self):
        """for debugging and printing"""
        return "{}/{} - {}".format(self.quantity, self.dealer_or_broker_id,
                                   self.order_id)

    @property
    def limit(self):
        """to ensure it lands in front of the list"""
        if self._side == Side.ASK:
            retval = 0
        else:
            retval = float('inf')

        return retval
