from dataclasses import asdict
from market.quote import Quote


class TestQuote:
    def test_dictionary(self):
        quote = Quote(type="limit", dealer_or_broker_id="foo", symbol="bar",
                      side="bid", quantity=100, price=5.12)
        assert asdict(quote) == {"type": "limit",
                                 "dealer_or_broker_id": "foo",
                                 "symbol": "bar",
                                 "side": "bid",
                                 "quantity": 100,
                                 "price": 5.12}
