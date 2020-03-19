import unittest
from math import log, sqrt, exp
from datetime import date, timedelta

from scipy.stats import norm

from options.option_style import OptionStyle
from term_structures.curve import Curve
from term_structures.surface import Surface
from utils.date.yearfrac import day_count, DayCntCnvEnum
from utils.parameters.environment import Environment


class BlackScholesPricer:
    def __init__(self,
                 spot: float,
                 strike: float,
                 discount_curve: Curve,
                 volatility_surface: Surface,
                 valuation_date: date,
                 maturity_date: date,
                 convention: DayCntCnvEnum = DayCntCnvEnum.basis_30_360_isda,
                 style: OptionStyle = OptionStyle.CALL):

        self.spot = spot
        self.strike = strike
        self.discount_curve = discount_curve
        self.volatility_surface = volatility_surface
        self.valuation_date = valuation_date
        self.maturity_date = maturity_date
        self.day_count_convention = day_count(convention)
        self.style = style

    @property
    def time_to_maturity(self) -> float:
        return self.day_count_convention.year_fraction(self.valuation_date,
                                                       self.maturity_date)

    @property
    def interest_rate(self) -> float:
        return self.discount_curve(self.time_to_maturity)

    @property
    def volatility(self) -> float:
        return self.volatility_surface(self.time_to_maturity, self.strike)

    def calculate(self) -> float:
        sig = self.volatility
        t = self.time_to_maturity
        r = self.interest_rate
        s = self.spot
        k = self.strike

        d1 = (log(s/k) + (r + 0.5 * (sig ** 2)) * t) / (sig * sqrt(t))
        d2 = d1 - sig * sqrt(t)

        cp = float(self.style)
        n = norm.cdf

        return cp * s * n(cp * d1) - cp * k * exp(-r * t) * n(cp * d2)


class TestBS(unittest.TestCase):
    def setUp(self):
        self.env = Environment()
        self.env.add_constant("daycount",
                              DayCntCnvEnum.basis_30_360_isda)
        self.env.valuation_date = date(2019, 7, 23)

    def test_contract(self):
        self.env.add_curve("curve", Curve([0.001, 1, 2],
                                          [0.01, 0.05, 0.1]))
        self.env.add_surface("surface",
                             Surface([0.01, 1, 2], [95.0, 100.0, 105.0],
                                     [[0.25, 0.25, 0.25],
                                     [0.25, 0.25, 0.25],
                                     [0.25, 0.25, 0.25]]))
        spot = 50.0
        strike = 100.0
        expiry_date = date(2020, 7, 23)

        contract = BlackScholesPricer(spot,
                                      strike,
                                      self.env.get_curve("curve"),
                                      self.env.get_surface("surface"),
                                      self.env.valuation_date,
                                      expiry_date,
                                      self.env.get_constant("daycount"),
                                      OptionStyle.CALL)
        self.assertEqual(contract.calculate(), 0.027352509369436284)

        contract = BlackScholesPricer(spot,
                                      strike,
                                      self.env.get_curve("curve"),
                                      self.env.get_surface("surface"),
                                      self.env.valuation_date,
                                      expiry_date,
                                      self.env.get_constant("daycount"),
                                      OptionStyle.PUT)
        self.assertEqual(contract.calculate(), 45.150294959440842)

    def test_other_contract(self):
        self.env.add_curve("curve", Curve([0.001, 1, 2],
                                          [0.1, 0.1, 0.1]))
        self.env.add_surface("surface", Surface([0.01, 1, 2],
                                                [35.0, 40.0, 45.0],
                                                [[0.15, 0.15, 0.15],
                                                 [0.2, 0.2, 0.2],
                                                 [0.251, 0.252, 0.253]]))
        spot = 42.0
        strike = 40.0
        expiry_date = self.env.valuation_date + timedelta(days=181)

        contract = BlackScholesPricer(spot,
                                      strike,
                                      self.env.get_curve("curve"),
                                      self.env.get_surface("surface"),
                                      self.env.valuation_date,
                                      expiry_date,
                                      self.env.get_constant("daycount"),
                                      OptionStyle.CALL)
        self.assertEqual(contract.calculate(), 4.721352072007573)

        contract = BlackScholesPricer(spot,
                                      strike,
                                      self.env.get_curve("curve"),
                                      self.env.get_surface("surface"),
                                      self.env.valuation_date,
                                      expiry_date,
                                      self.env.get_constant("daycount"),
                                      OptionStyle.PUT)
        self.assertEqual(contract.calculate(), 0.8022499147099111)


if __name__ == '__main__':
    unittest.main()
