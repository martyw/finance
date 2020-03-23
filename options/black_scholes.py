import unittest
import logging
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

    @property
    def price(self) -> float:
        return BlackScholesPricer.bs_price(self.style,
                                           self.spot,
                                           self.strike,
                                           self.time_to_maturity,
                                           self.interest_rate,
                                           self.volatility)

    @staticmethod
    def bs_price(call_put_flag: int, spot: float, strike: float,
                 time_to_maturity: float, interest_rate: float,
                 volatility: float):
        assert call_put_flag == -1 or call_put_flag == 1
        sig = volatility
        t = time_to_maturity
        r = interest_rate
        s = spot
        k = strike

        d1 = (log(s/k) + (r + 0.5 * (sig ** 2)) * t) / (sig * sqrt(t))
        d2 = d1 - sig * sqrt(t)

        cp = call_put_flag
        n = norm.cdf

        return cp * s * n(cp * d1) - cp * k * exp(-r * t) * n(cp * d2)

    @property
    def vega(self):
        return BlackScholesPricer.bs_vega(self.spot,
                                          self.strike,
                                          self.time_to_maturity,
                                          self.interest_rate,
                                          self.volatility)

    @staticmethod
    def bs_vega(spot: float, strike: float,time_to_maturity: float,
                interest_rate: float, volatility: float):
        sig = volatility
        t = time_to_maturity
        r = interest_rate
        s = spot
        k = strike
        n = norm.pdf

        d1 = (log(s/k)+(r+sig*sig/2.)*t)/(sig*sqrt(t))

        return s * sqrt(t)*n(d1)

    @staticmethod
    def implied_vol(observed_price: float, call_put_flag: int, spot: float,
                    strike: float, time_to_maturity: float,
                    interest_rate: float):

        assert call_put_flag == -1 or call_put_flag == 1
        MAX_ITERATIONS = 100
        PRECISION = 1.0e-5

        sigma = 0.5 # guess
        for i in range(0, MAX_ITERATIONS):
            price = BlackScholesPricer.bs_price(call_put_flag, spot, strike,
                                                time_to_maturity,
                                                interest_rate, sigma)
            vega = BlackScholesPricer.bs_vega(spot, strike, time_to_maturity,
                                              interest_rate, sigma)

            price = price
            diff = observed_price - price  # our root

            logging.debug(i, sigma, diff)

            if abs(diff) < PRECISION:
                return sigma
            sigma = sigma + diff/vega # f(x) / f'(x)

        # value wasn't found, return best guess so far
        return sigma

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
        self.assertEqual(contract.price, 0.027352509369436284)

        contract = BlackScholesPricer(spot,
                                      strike,
                                      self.env.get_curve("curve"),
                                      self.env.get_surface("surface"),
                                      self.env.valuation_date,
                                      expiry_date,
                                      self.env.get_constant("daycount"),
                                      OptionStyle.PUT)
        self.assertEqual(contract.price, 45.150294959440842)

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
        self.assertEqual(contract.price, 4.721352072007573)

        contract = BlackScholesPricer(spot,
                                      strike,
                                      self.env.get_curve("curve"),
                                      self.env.get_surface("surface"),
                                      self.env.valuation_date,
                                      expiry_date,
                                      self.env.get_constant("daycount"),
                                      OptionStyle.PUT)
        self.assertEqual(contract.price, 0.8022499147099111)

    def test_implied_vol(self):
        dc = day_count(DayCntCnvEnum.basis_act_365_fixed)

        V_market = 17.5
        K = 585
        T = dc.year_fraction(date(2014, 9, 8), date(2014, 10, 18))
        S = 586.08
        r = 0.0002
        cp = OptionStyle.CALL

        implied_vol = BlackScholesPricer.implied_vol(V_market,
                                                     int(cp),
                                                     S, K, T, r)
        self.assertEqual(implied_vol, 0.21921383628613422)

if __name__ == '__main__':
    unittest.main()
