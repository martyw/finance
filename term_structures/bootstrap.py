""" Bootstrapping the yield curve """
import unittest
from math import log, exp
from typing import List

from securities.bond import Bond
from term_structures.curve import Curve


class BootstrappedCurve(Curve):
    """
    Bootstrap a curve of bond instruments to zero coupon rates
    """
    def __init__(self):
        self._instruments = {}  # Map each maturity to an instrument
        super().__init__({})

    def add_instrument(self, bond):
        """ Save instrument info by maturity """
        self._curve[bond.maturity_term] = None
        self._instruments[bond.maturity_term] = bond

    @property
    def rates(self) -> List:
        """ Calculate list of available zero rates """
        for bond in self._instruments.values():
            if bond.maturity_term not in self._curve:
                raise KeyError("term {} not found in curve".format(bond.maturity_term))
            self._curve[bond.maturity_term] = self.bond_spot_rate(bond)

        return [self._curve[t] for t in self.times]

    def bond_spot_rate(self, bond: Bond) -> float:
        """ return the spot rate for the input bond """
        if bond.coupon == 0:
            # get rate of a zero coupon bond
            spot_rate = log(bond.par / bond.price) / bond.maturity_term
        else:
            # calculate spot rate of a bond
            number_of_periods = \
                int(bond.maturity_term * bond.compounding_frequency)
            value = bond.price
            cpn_payment = bond.coupon * bond.par / bond.compounding_frequency

            for i in range(1, number_of_periods):
                term = i / float(bond.compounding_frequency)
                rate = self._curve[term]
                discounted_coupon_value = cpn_payment * exp(-rate * term)
                value -= discounted_coupon_value

            last = number_of_periods / float(bond.compounding_frequency)
            spot_rate = -log(value / (bond.par + cpn_payment)) / last

        return spot_rate


class TestBootstrap(unittest.TestCase):
    """test bootstrapping"""
    def setUp(self):
        """initialize the test curve"""
        self.yield_curve = BootstrappedCurve()
        self.yield_curve.add_instrument(Bond(100, 0.25, 0., 97.5))
        self.yield_curve.add_instrument(Bond(100, 0.5, 0., 94.9))
        self.yield_curve.add_instrument(Bond(100, 1.0, 0., 90.))
        self.yield_curve.add_instrument(Bond(100, 1.5, 8.0, 96., 2))
        self.yield_curve.add_instrument(Bond(100, 2., 12.0, 101.6, 2))

    def test_maturities(self):
        """test maturity terms of the curve points"""
        self.assertEqual(self.yield_curve.times, [0.25, 0.5, 1.0, 1.5, 2.0])

    def test_bootstrap(self):
        """test bootstrap"""
        rates = {0.25: 0.10127123193715915,
                 0.5: 0.10469296074441839,
                 1.0: 0.10536051565782635,
                 1.5: 0.1068092638817053,
                 2.0: 0.10808027549746793}
        self.assertEqual(self.yield_curve.rates, list(rates.values()))

    def test_interpolator(self):
        """test interpolation"""
        for term in self.yield_curve.times:
            point = self.yield_curve[term]
            interp = self.yield_curve.loglinear_interpolate(term)

            self.assertEqual(point, interp)

    def test_string_representation(self):
        expected = "{0.25: 0.10127123193715915, 0.5: 0.10469296074441839, 1.0: 0.10536051565782635, 1.5: 0.1068092638817053, 2.0: 0.10808027549746793}"  # noqa
        self.assertEqual(str(self.yield_curve), expected)


if __name__ == '__main__':
    unittest.main()
