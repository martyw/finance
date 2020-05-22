"""
Model for a curve made of time/value points with an interpolator
"""
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
