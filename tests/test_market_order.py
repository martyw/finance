import unittest
from market.quote import Quote
from market.market_order import MarketOrder
from dataclasses import asdict


class TestAlgoSim(unittest.TestCase):
    def setUp(self):
        ask_quote = Quote(type='market', side='ask', quantity=40,
                          dealer_or_broker_id=111)
        self.ask_order = MarketOrder(asdict(ask_quote))
        bid_quote = Quote(type='market', side='bid', quantity=40,
                          dealer_or_broker_id=111)
        self.bid_order = MarketOrder(asdict(bid_quote))

    def test_fields(self):
        self.assertEqual(self.ask_order["type"], "market")
        self.assertEqual(self.ask_order["quantity"], 40)

    def test_string_representation(self):
        self.assertEqual(str(self.ask_order)[0:6], "40/111")

    def test_limit(self):
        self.assertEqual(self.ask_order.limit, 0.0)
        self.assertEqual(self.bid_order.limit, float("inf"))
