import csv
import logging
import os.path
import unittest
from dataclasses import asdict
from market.quote import Quote
from orderbook.matching_engine import MatchingEngine
from position_keeping.trade import Trade


class TestAlgoSim(unittest.TestCase):
    """implements test case from algosim.py
    """

    def setUp(self):
        """set up of orderbook as found in input.csv
        """
        script_dir = os.path.dirname(__file__)
        logging.debug('**** TestAlgoSim:setUp')
        self.order_book = MatchingEngine()
        with open(os.path.join(script_dir, 'orders_test1.txt')) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.order_book.match_order(row)

        # orderbook
        #               BID                                     ASK
        #  order id     broker     limit   quantity     | order id     broker     limit   quantity  # noqa
        #       1           AB      1.00    15000       |       6       JF          1.02    31000   # noqa
        #       2           AB      1.00    15000       |       7       ML          1.04     5000   # noqa
        #       3           CD      0.99     5000       |       8       SC          1.05     2000   # noqa
        #       4           EF      0.98     3000       |       9       HS          1.09     2000   # noqa
        #       5          ABC      0.97    12000       |

    def test_add_limit_order(self):
        """the testcase from myalgo.py
        """
        logging.debug('**** TestAlgoSim:test_add_limit_order')
        self.assertEqual(len(self.order_book.bids), 5)
        self.assertEqual(len(self.order_book.asks), 4)

        # orderbook
        #               BID                                     ASK
        #  order id     broker     limit   quantity     | order id     broker     limit   quantity  # noqa
        #      10           ME      1.04    10000       |
        #       1           AB      1.00    15000       |       6       JF          1.02    31000   # noqa
        #       2           AB      1.00    15000       |       7       ML          1.04     5000   # noqa
        #       3           CD      0.99     5000       |       8       SC          1.05     2000   # noqa
        #       4           EF      0.98     3000       |       9       HS          1.09     2000   # noqa
        #       5          ABC      0.97    12000       |

        quote = Quote(type='limit',
                      side='bid',
                      quantity=10000,
                      price=1.04,
                      dealer_or_broker_id='ME')
        (trades, order) = self.order_book.match_order(asdict(quote))
        # orderbook
        #
        #               BID                                     ASK
        #  order id     broker     limit   quantity     | order id     broker     limit   quantity  # noqa
        #                                               |
        #       1           AB      1.00    15000       |      11       JF          1.02    21000   # noqa
        #       2           AB      1.00    15000       |       7       ML          1.04     5000   # noqa
        #       3           CD      0.99     5000       |       8       SC          1.05     2000   # noqa
        #       4           EF      0.98     3000       |       9       HS          1.09     2000   # noqa
        #       5          ABC      0.97    12000       |
        #
        # tape
        #
        # bought  sold  quantity price
        #   ME     JF    10000   1.02

        self.assertEqual(len(trades), 1)
        trade = trades[0]
        self.assertEqual(type(trade), Trade)
        self.assertEqual(trade['buyer'], 'ME')
        self.assertEqual(trade['seller'], 'JF')
        self.assertEqual(trade['price'], 1.02)
        self.assertEqual(trade['quantity'], 10000)
        self.assertIsNone(order)

        self.assertEqual(len(self.order_book.bids), 5)
        self.assertEqual(len(self.order_book.asks), 4)


class TestExample(unittest.TestCase):
    """ implements test case from example.py and some additional tests
    """
    def setUp(self):
        logging.debug('**** TestExample:setUp')
        self.order_book = MatchingEngine()
        script_dir = os.path.dirname(__file__)
        with open(os.path.join(script_dir, 'orders_test2.txt')) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.order_book.match_order(row)
        # orderbook
        #               BID                                     ASK
        #  order id     broker     limit   quantity     | order id     broker     limit   quantity  # noqa
        #                                               |
        #       5           AA      99      5           |       1       AA          101         5   # noqa
        #       7           CC      99      5           |       3       CC          101         5   # noqa
        #       6           BB      98      5           |       4       DD          101         5   # noqa
        #       8           DD      97      5           |       2       BB          103         5   # noqa
        #                                               |
        # tape
        #
        # bought  sold  quantity price
        #

    def test_crossing_limit_order(self):
        """ this order will result in a trade
        """
        logging.debug('**** TestExample:test_crossing_limit_order')
        self.assertEqual(len(self.order_book.bids), 4)
        self.assertEqual(len(self.order_book.asks), 4)
        crossing_limit_order = Quote(type='limit',
                                     side='bid',
                                     quantity=2,
                                     price=102,
                                     dealer_or_broker_id='EE')

        # orderbook
        #               BID                                     ASK
        #  order id     broker     limit   quantity     | order id     broker     limit   quantity  # noqa
        #       9           EE     102      2           |
        #       5           AA      99      5           |       1       AA          101         5   # noqa
        #       7           CC      99      5           |       3       CC          101         5   # noqa
        #       6           BB      98      5           |       4       DD          101         5   # noqa
        #       8           DD      97      5           |       2       BB          103         5   # noqa
        #                                               |
        # tape
        #
        # bought  sold  quantity price
        #
        (trades, new_order_in_book) = \
            self.order_book.match_order(asdict(crossing_limit_order))
        # orderbook
        #               BID                                     ASK
        #  order id     broker     limit   quantity     | order id     broker     limit   quantity  # noqa
        #                                               |
        #       5           AA      99      5           |      10       AA          101         3   # noqa
        #       7           CC      99      5           |       3       CC          101         5   # noqa
        #       6           BB      98      5           |       4       DD          101         5   # noqa
        #       8           DD      97      5           |       2       BB          103         5   # noqa
        #                                               |
        # tape
        #
        # bought  sold  quantity price
        #   EE     AA       2     101

        self.assertEqual(len(trades), 1)
        self.assertIsNone(new_order_in_book)
        trade = trades[0]
        self.assertEqual(trade['price'], 101)
        self.assertEqual(trade['quantity'], 2)

        self.assertEqual(len(self.order_book.bids), 4)
        self.assertEqual(len(self.order_book.asks), 4)

    def test_big_crossing_limit_order(self):
        """ order is bigger than available liquidity
        """
        logging.debug('**** TestExample:test_big_crossing_limit_order')
        self.assertEqual(len(self.order_book.bids), 4)
        self.assertEqual(len(self.order_book.asks), 4)
        big_crossing_limit_order = Quote(type='limit',
                                         side='bid',
                                         quantity=50,
                                         price=102,
                                         dealer_or_broker_id='EE')
        # orderbook
        #               BID                                     ASK
        #  order id     broker     limit   quantity     | order id     broker     limit   quantity  # noqa
        #       9           EE     102     50                                        |              # noqa
        #       5           AA      99      5           |       1       AA          101         5   # noqa
        #       7           CC      99      5           |       3       CC          101         5   # noqa
        #       6           BB      98      5           |       4       DD          101         5   # noqa
        #       8           DD      97      5           |       2       BB          103         5   # noqa
        #                                               |
        # tape
        #
        # bought  sold  quantity price
        #

        (trades, new_order_in_book) = \
            self.order_book.match_order(asdict(big_crossing_limit_order))
        # orderbook
        #               BID                                     ASK
        #  order id     broker     limit   quantity     | order id     broker     limit   quantity  # noqa
        #      10           EE     102     35           |
        #       5           AA      99      5           |
        #       7           CC      99      5           |
        #       6           BB      98      5           |
        #       8           DD      97      5           |       2       BB          103         5   # noqa
        #                                               |
        # tape
        #
        # bought  sold  quantity price
        #   EE     AA       5     101
        #   EE     CC       5     101
        #   EE     DD       5     101

        self.assertEqual(new_order_in_book['price'], 102)
        self.assertEqual(new_order_in_book['trade_id'], 'EE')
        self.assertEqual(new_order_in_book['type'], 'limit')
        self.assertEqual(new_order_in_book['side'], 'bid')
        self.assertEqual(new_order_in_book['quantity'], 35)

        self.assertEqual(len(trades), 3)

        trade = trades[0]
        self.assertEqual(trade['buyer'], 'EE')
        self.assertEqual(trade['seller'], 'AA')
        self.assertEqual(trade['price'], 101)
        self.assertEqual(trade['quantity'], 5)

        self.assertEqual(len(self.order_book.bids), 5)
        self.assertEqual(len(self.order_book.asks), 1)

    def test_market_order(self):
        """ test a marketorder
        """
        logging.debug('**** TestExample:test_market_order')
        self.assertEqual(len(self.order_book.bids), 4)
        self.assertEqual(len(self.order_book.asks), 4)
        # orderbook
        #               BID                                     ASK
        #  order id     broker     limit   quantity     | order id     broker     limit   quantity  # noqa
        #                     |
        #       5           AA      99      5           |       1       AA          101         5   # noqa
        #       7           CC      99      5           |       3       CC          101         5   # noqa
        #       6           BB      98      5           |       4       DD          101         5   # noqa
        #       8           DD      97      5           |       2       BB          103         5   # noqa
        #                                               |
        # tape
        #
        # bought  sold  quantity price
        #

        market_order = Quote(type='market',
                             side='ask',
                             quantity=40,
                             dealer_or_broker_id=111)
        # orderbook
        #               BID                                     ASK
        #  order id     broker     limit   quantity     | order id     broker     limit   quantity  # noqa
        #                                               |       9      111                     40   # noqa
        #       5           AA      99      5           |       1       AA          101         5   # noqa
        #       7           CC      99      5           |       3       CC          101         5   # noqa
        #       6           BB      98      5           |       4       DD          101         5   # noqa
        #       8           DD      97      5           |       2       BB          103         5   # noqa
        #                                               |
        # tape
        #
        # bought  sold  quantity price
        #
        (trades, _) = self.order_book.match_order(asdict(market_order))
        # orderbook
        #               BID                                     ASK
        #  order id     broker     limit   quantity     | order id     broker     limit   quantity  # noqa
        #                                               |       9      111                     20   # noqa
        #                                               |       1       AA          101         5   # noqa
        #                                               |       3       CC          101         5   # noqa
        #                                               |       4       DD          101         5   # noqa
        #                                               |       2       BB          103         5   # noqa
        #                                               |
        # tape
        #
        # bought  sold  quantity price
        #  AA       111   5       99
        #  CC       111   5       99
        #  BB       111   5       98
        #  DD       111   5       97

        self.assertEqual(len(trades), 4)
        self.assertEqual(len(self.order_book.bids), 0)
        self.assertEqual(len(self.order_book.asks), 5)

    def test_utility_functions(self):
        """ test orderbook attributes retrieval functions
        """
        # orderbook
        #               BID                                     ASK
        #  order id     broker     limit   quantity     | order id     broker     limit   quantity  # noqa
        #                                               |
        #       5           AA      99      5           |       1       AA          101         5   # noqa
        #       7           CC      99      5           |       3       CC          101         5   # noqa
        #       6           BB      98      5           |       4       DD          101         5   # noqa
        #       8           DD      97      5           |       2       BB          103         5   # noqa
        #                                               |
        # tape
        #
        # bought  sold  quantity price
        #

        logging.debug('**** TestExample:test_utility_functions')
        self.assertEqual(self.order_book.get_best_bid(), 99)
        self.assertEqual(self.order_book.get_worst_bid(), 97)
        self.assertEqual(str(self.order_book.asks[0]), "5@101.0/AA - 50")
        self.assertEqual(self.order_book.get_best_ask(), 101)
        self.assertEqual(self.order_book.get_worst_ask(), 103)
        self.assertEqual(self.order_book.get_volume_at_price('ask', 103),
                         5)
        self.assertEqual(self.order_book.get_volume_at_price('bid', 97),
                         5)
        self.assertEqual(self.order_book.get_volume_at_price('ask', 101),
                         15)

    def test_robustness(self):
        """ test exceptions
        """
        # orderbook
        #               BID                                     ASK
        #  order id     broker     limit   quantity     | order id     broker     limit   quantity  # noqa
        #                                               |
        #       5           AA      99      5           |       1       AA          101         5   # noqa
        #       7           CC      99      5           |       3       CC          101         5   # noqa
        #       6           BB      98      5           |       4       DD          101         5   # noqa
        #       8           DD      97      5           |       2       BB          103         5   # noqa
        #                                               |
        # tape
        #
        # bought  sold  quantity price
        #

        logging.debug('**** TestExample:test_robustness')
        order = {'type': 'limit'}
        with self.assertRaises(AssertionError):
            self.order_book.match_order(order)
        with self.assertRaises(KeyError):
            self.order_book.get_volume_at_price('qwerty', 97)
        with self.assertRaises(AssertionError):
            bad_order = {'type': 'limit',
                         'side': 'ask',
                         'quantity': 23,
                         'trade_id': 111}
            (_, _) = self.order_book.match_order(bad_order)
        with self.assertRaises(AssertionError):
            bad_order = {'type': 'limit',
                         'side': 'ask',
                         'quantity': -1,
                         'price': 100,
                         'trade_id': 123}
            (_, _) = self.order_book.match_order(bad_order)
        with self.assertRaises(KeyError):
            bad_order = {'type': 'limit',
                         'side': 'asdf',
                         'quantity': -1,
                         'price': 100,
                         'trade_id': 123}
            (_, _) = self.order_book.match_order(bad_order)
        with self.assertRaises(KeyError):
            bad_order = {'type': 'gtc',
                         'side': 'ask',
                         'quantity': -1,
                         'price': 100,
                         'trade_id': 123}
            (_, _) = self.order_book.match_order(bad_order)
