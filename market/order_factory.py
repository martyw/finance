"""
order factory method
"""
from market.market_order import MarketOrder
from market.limit_order import LimitOrder


def create_order(quote):
    """factory method to create order object from input dictionary"""
    assert 'type' in quote

    if quote['type'] == 'limit':
        retval = LimitOrder(quote)
    elif quote['type'] == 'market':
        retval = MarketOrder(quote)
    else:
        raise KeyError('Unknown order type %s' % quote['type'])

    return retval
