"""
trade
"""
from market.order import Order
from market.market_order import MarketOrder
from market.limit_order import LimitOrder
from market.side import Side


class Trade:
    """trade based on order and matching order from book"""
    def __init__(self, order: Order, matched_order: Order):
        """calculate traded quantity based on order and matched order size
        """
        self.order = order
        self.matched_order = matched_order

        # set trade quantity
        if self.order.quantity < self.matched_order.quantity:
            self._quantity = self.order.quantity
        else:
            self._quantity = self.matched_order.quantity

        if isinstance(order, MarketOrder):
            self._price = matched_order.limit
        elif isinstance(order, LimitOrder):
            if order.limit > matched_order.limit:
                self._price = matched_order.limit
            else:
                self._price = order.limit
        else:
            raise RuntimeWarning("unexpcted order type {}".
                                 format(type(order).__name__))

    @property
    def quantity(self) -> int:
        return self._quantity

    @property
    def price(self) -> float:
        return self._price

    def __repr__(self):
        """for debugging and printing"""
        attributes = (self.quantity,
                      self.matched_order.limit,
                      self.order.order_id,
                      self.matched_order.order_id,
                      self.order.dealer_or_broker_id,
                      self.matched_order.dealer_or_broker_id)

        return '%s @ %s (%s/%s) %s/%s' % attributes

    def __getitem__(self, item: str):
        """for querying properties in dict style"""
        if item == 'price':
            return self.matched_order.limit

        if item == 'quantity':
            return self.quantity

        if item == 'buyer':
            if self.order.side == Side.BID:
                buyer = self.order.dealer_or_broker_id
            else:
                buyer = self.matched_order.dealer_or_broker_id

            return buyer

        if item == 'seller':
            if self.order.side == Side.BID:
                seller = self.matched_order.dealer_or_broker_id
            else:
                seller = self.order.dealer_or_broker_id

            return seller

        raise KeyError('Item %s can not be queried in Trade object' % item)
