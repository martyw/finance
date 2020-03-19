"""
Get a list of forward rates
starting from the second time period
"""
import unittest
from term_structures.curve import Curve


class ForwardRates(Curve):
    """ forward rates calculation"""
    def __init__(self):
        self.spot_rates = dict()
        super().__init__([], [])

    def add_spot_rate(self, term, spot_rate):
        """ initializing with spot rates"""
        self.spot_rates[term] = spot_rate

    @property
    def factors(self):
        """return the list of forward rates implied by the spot rates"""
        forward_rates = []
        periods = sorted(self.spot_rates.keys())
        for term2, term1 in zip(periods, periods[1:]):
            forward_rate = self.calculate_forward_rate(term1, term2)
            forward_rates.append(forward_rate)

        return forward_rates

    def calculate_forward_rate(self, term1, term2):
        """ the calculation itself"""
        rate1 = self.spot_rates[term1]
        rate2 = self.spot_rates[term2]
        forward_rate = (rate2 * term2 - rate1 * term1) / (term2 - term1)

        return forward_rate


class TestBootstrap(unittest.TestCase):
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


if __name__ == '__main__':
    unittest.main()
