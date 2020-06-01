import unittest
from term_structures.forward_rates import ForwardRates


class TestForwardCurve(unittest.TestCase):
    """test forward rate calculation"""
    def setUp(self):
        """initialize the test curve"""
        self.forward_rates = ForwardRates()
        self.forward_rates.add_spot_rate(0.25, 10.127)
        self.forward_rates.add_spot_rate(0.50, 10.469)
        self.forward_rates.add_spot_rate(1.00, 10.536)
        self.forward_rates.add_spot_rate(1.50, 10.681)
        self.forward_rates.add_spot_rate(2.00, 10.808)

    def test(self):
        """the test"""
        self.assertEqual(self.forward_rates.factors, [10.810999999999998,
                                                      10.603, 10.971, 11.189])
