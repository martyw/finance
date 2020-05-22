import unittest
from term_structures.bootstrap import BootstrappedCurve
from securities.bond import Bond


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
