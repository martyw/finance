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
    def __init__(self, times, factors):
        self._times = times
        self._factors = factors

    @property
    def times(self) -> List[float]:
        """to support overwrites when class is used as base"""
        return self._times

    @times.setter
    def times(self, val: List[float]):
        self._times = val

    @property
    def factors(self) -> List[float]:
        """to support overwrites when class is used as base"""
        return self._factors

    @factors.setter
    def factors(self, val: List[float]):
        self._factors = val

    def loglinear_interpolate(self, time_arg: float) -> float:
        """interpolator, loglinear"""
        log_time_arg = log10(time_arg)
        log_times = log10(self.times)
        log_factors = log10(self.factors)

        return 10.0 ** interp(log_time_arg, log_times, log_factors)

    def __call__(self, time_arg: float) -> float:
        """call the interpolator"""
        return float(self.loglinear_interpolate(time_arg))


class TestCurve(unittest.TestCase):
    """
    Test Curve class
    """
    def test_curve(self):
        """test method"""
        times = range(1, 4)
        factors = [exp(-0.05*t) for t in times]
        crv = Curve(times, factors)
        discount_factors = [crv(t) for t in times]
        self.assertEqual(discount_factors, [0.951229424500714,
                                            0.9048374180359595,
                                            0.8607079764250578])


if __name__ == '__main__':
    unittest.main()
