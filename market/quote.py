"""
utility class to set proper attributes for Order class
"""
from dataclasses import dataclass, asdict


@dataclass
class Quote:
    type: str
    dealer_or_broker_id: str
    side: str
    quantity: int
    price: float = 0.0
    symbol: str = None


if __name__ == "__main__":
    from market.limit_order import LimitOrder
    quote = Quote(type="limit", dealer_or_broker_id="foo", symbol="bar",
                  side="bid", quantity=100, price=5.12)
    order = LimitOrder(asdict(quote))
    print(order)
