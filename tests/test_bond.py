import unittest
from securities.bond import Bond


class TestBond(unittest.TestCase):
    """test bond functionality"""

    def setUp(self):
        """initialize the test bonds"""
        self.bond_with_known_price = Bond(100, 1.5, 5.75, 95.0428, None, 2)
        self.bond_with_known_ytm = Bond(100, 1.5, 5.75, None,
                                        0.09369155345239477, 2)
        self.another_bond_with_known_price = Bond(100, 2.5, 5.0,
                                                  95.92, None, 2)
        self.one_more_bond_with_known_price = Bond(100, 10.0, 6.0,
                                                   None, 0.08, 2)

    def test_ytm(self):
        """test yield to maturity calculation"""
        self.assertEqual(0.093691553452,
                         round(self.bond_with_known_price.yield_to_maturity,
                               12))
        self.assertEqual(0.06802229654625709,
                         self.another_bond_with_known_price.yield_to_maturity)

    def test_price(self):
        """test price calculation"""
        self.assertEqual(95.0428, round(self.bond_with_known_ytm.price, 4))

    def test_mduration(self):
        """test modified duration calculation"""
        self.assertEqual(1.392,
                         round(self.bond_with_known_price.mod_duration, 3))
        self.assertEqual(7.178422566280552,
                         self.one_more_bond_with_known_price.mod_duration)

    def test_convexity(self):
        """test convexity calculation"""
        self.assertEqual(2.6339593903,
                         round(self.bond_with_known_price.convexity, 10))

    def test_initialization_errors(self):
        with self.assertRaises(TypeError):
            # argument should be a dict
            b = Bond.from_dict([1, 2])
        with self.assertRaises(KeyError):
            # wrong argument 'compounding', should be 'compounding_frequency'
            b = Bond.from_dict({"par": 100.0,
                                "maturity_term": 2.5,
                                "coupon": 0.5,
                                "ytm": 0.003,
                                "compounding": 2})
        with self.assertRaises(KeyError):
            # omitted mandatory key 'par'
            b = Bond.from_dict({"maturity_term": 2.5,
                                "coupon": 0.5,
                                "ytm": 0.003,
                                "compounding_frequency": 2})
