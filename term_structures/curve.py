"""
Model for a curve made of time/value points with an interpolator
"""
import unittest
from math import exp
from typing import List

from numpy import interp, log10


class Curve:
    """
    Curve class
    """
    def __init__(self, curve):
        self._curve = dict(curve) # maturity -> rate map

    @property
    def times(self) -> List[float]:
        return sorted(self._curve.keys())

    @property
    def rates(self) -> List[float]:
        """to support overwrites when class is used as base"""
        return [self._curve[tm] for tm in self.times]

    def __getitem__(self, item):
        # make sure the internal data structure self._curve is populated
        if not self.rates:
            dummy = self.rates
        return self._curve[item]

    @property
    def discount_factors(self):
        return [Curve.discount_factor(tm, self._curve[tm]) for tm in self.times]

    @staticmethod
    def discount_factor(time: float, rate: float):
        return exp(-1.0 * rate * time)

    def loglinear_interpolate(self, time_arg: float) -> float:
        """interpolator, loglinear"""
        if time_arg == 0.0:
            time_arg = 1e-12
        log_time_arg = log10(time_arg)
        log_times = log10(self.times)
        log_factors = log10(self.rates)

        return 10.0 ** interp(log_time_arg, log_times, log_factors)

    def __call__(self, time_arg: float) -> float:
        """call the interpolator"""
        return float(self.loglinear_interpolate(time_arg))

    def __repr__(self):
        # make sure the internal data structure self._curve is populated
        if not self.rates:
            dummy = self.rates
        return str(self._curve)


class TestCurve(unittest.TestCase):
    """
    Test Curve class
    """
    def setUp(self) -> None:
        self.discount_curve = Curve({0.5: 0.0378,
                                     1.0: 0.0389,
                                     1.5: 0.0401,
                                     2.0: 0.0413,
                                     2.5: 0.0425,
                                     3.0: 0.04375,
                                     3.5: 0.0450})

    def test_discount(self):
        df = [0.9812774850850906, 0.9618468890261952, 0.9416232794985323,
              0.9207193613169226, 0.8991998200185832, 0.876998497358217,
              0.8542768136084795]
        self.assertEqual(self.discount_curve.discount_factors, df)

    def test_string(self):
        string_value = "{0.5: 0.0378, 1.0: 0.0389, 1.5: 0.0401, 2.0: 0.0413, 2.5: 0.0425, 3.0: 0.04375, 3.5: 0.045}"    # noqa
        self.assertEqual(str(self.discount_curve), string_value)

    def test_curve(self):
        """test method"""
        times = range(1, 4)
        factors = [exp(-0.05*t) for t in times]
        crv = Curve(zip(times, factors))
        self.assertEqual(crv.rates, [0.951229424500714,
                                     0.9048374180359595,
                                     0.8607079764250578])


if __name__ == '__main__':
    unittest.main()

