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

MAX_ITERATIONS = 100
PLACES = 5
PRECISION = 10**-PLACES


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
        return BlackScholesPricer.calculate_price(call_put_flag=self.style,
                                                  spot=self.spot,
                                                  strike=self.strike,
                                                  time_to_maturity=self.time_to_maturity,   # noqa
                                                  interest_rate=self.interest_rate,         # noqa
                                                  volatility=self.volatility)

    @staticmethod
    def calculate_price(call_put_flag: int, spot: float, strike: float,
                        time_to_maturity: float, interest_rate: float,
                        volatility: float) -> float:
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
    def vega(self) -> float:
        return BlackScholesPricer.calculate_vega(spot=self.spot,
                                                 strike=self.strike,
                                                 time_to_maturity=self.time_to_maturity,    # noqa
                                                 interest_rate=self.interest_rate,          # noqa
                                                 volatility=self.volatility)

    @staticmethod
    def calculate_vega(spot: float, strike: float, time_to_maturity: float,
                       interest_rate: float, volatility: float) -> float:
        sig = volatility
        t = time_to_maturity
        r = interest_rate
        s = spot
        k = strike
        n = norm.pdf

        d1 = (log(s/k)+(r+sig*sig/2.)*t)/(sig*sqrt(t))

        return s * sqrt(t)*n(d1)

    @staticmethod
    def implied_vol(observed_price: float,
                    call_put_flag: int,
                    spot: float,
                    strike: float,
                    time_to_maturity: float,
                    interest_rate: float) -> float:
        """solve for volatility with known observed price
        Newton-Raphson to approximate implied volatility"""
        assert call_put_flag == -1 or call_put_flag == 1

        sigma = 0.5     # initial guess
        i = 0
        diff = PRECISION + 1

        while i < MAX_ITERATIONS and abs(diff) > PRECISION:
            price = BlackScholesPricer.calculate_price(call_put_flag=call_put_flag,         # noqa
                                                       spot=spot,
                                                       strike=strike,
                                                       time_to_maturity=time_to_maturity,   # noqa
                                                       interest_rate=interest_rate,         # noqa
                                                       volatility=sigma)

            vega = BlackScholesPricer.calculate_vega(spot=spot,
                                                     strike=strike,
                                                     time_to_maturity=time_to_maturity,     # noqa
                                                     interest_rate=interest_rate,           # noqa
                                                     volatility=sigma)

            diff = observed_price - price   # root
            logging.debug(i, sigma, diff)
            sigma = sigma + diff/vega       # f(x) / f'(x)

            i += 1

        return sigma

    def implied_volatility(self, observed_price: float):
        return BlackScholesPricer.implied_vol(observed_price=observed_price,
                                              call_put_flag=int(self.style),
                                              spot=self.spot,
                                              strike=self.strike,
                                              time_to_maturity=self.time_to_maturity,   # noqa
                                              interest_rate=self.interest_rate)         # noqa


class TestBSPricer(unittest.TestCase):
    def setUp(self):
        self.env = Environment()
        self.env.add_constant("daycount",
                              DayCntCnvEnum.basis_30_360_isda)
        self.env.valuation_date = date(2019, 7, 23)

    def test_contract(self):
        self.env.add_curve("curve", Curve({0.001: 0.01 , 1: 0.05, 2: 0.1}))
        self.env.add_surface("surface",
                             Surface([0.01, 1, 2], [95.0, 100.0, 105.0],
                                     [[0.25, 0.25, 0.25],
                                     [0.25, 0.25, 0.25],
                                     [0.25, 0.25, 0.25]]))
        spot = 50.0
        strike = 100.0
        expiry_date = date(2020, 7, 23)

        contract = BlackScholesPricer(spot=spot,
                                      strike=strike,
                                      discount_curve=self.env.get_curve("curve"),           # noqa
                                      volatility_surface=self.env.get_surface("surface"),   # noqa
                                      valuation_date=self.env.valuation_date,
                                      maturity_date=expiry_date,
                                      convention=self.env.get_constant("daycount"),         # noqa
                                      style=OptionStyle.CALL)
        self.assertEqual(contract.price, 0.027352509369436284)

        implied = contract.implied_volatility(observed_price=0.0273525)
        self.assertAlmostEqual(implied, 0.25, places=PLACES)

        contract = BlackScholesPricer(spot=spot,
                                      strike=strike,
                                      discount_curve=self.env.get_curve("curve"),           # noqa
                                      volatility_surface=self.env.get_surface("surface"),   # noqa
                                      valuation_date=self.env.valuation_date,
                                      maturity_date=expiry_date,
                                      convention=self.env.get_constant("daycount"),         # noqa
                                      style=OptionStyle.PUT)
        self.assertEqual(contract.price, 45.150294959440842)
        self.assertAlmostEqual(implied, 0.25, places=PLACES)

    def test_other_contract(self):
        self.env.add_curve("curve", Curve({0.001: 0.1, 1: 0.1, 2: 0.1}))
        self.env.add_surface("surface", Surface([0.01, 1, 2],
                                                [35.0, 40.0, 45.0],
                                                [[0.15, 0.15, 0.15],
                                                 [0.2, 0.2, 0.2],
                                                 [0.251, 0.252, 0.253]]))
        spot = 42.0
        strike = 40.0
        expiry_date = self.env.valuation_date + timedelta(days=181)

        contract = BlackScholesPricer(spot=spot,
                                      strike=strike,
                                      discount_curve=self.env.get_curve("curve"),           # noqa
                                      volatility_surface=self.env.get_surface("surface"),   # noqa
                                      valuation_date=self.env.valuation_date,
                                      maturity_date=expiry_date,
                                      convention=self.env.get_constant("daycount"),         # noqa
                                      style=OptionStyle.CALL)
        price = 4.721352072007573
        self.assertEqual(contract.price, price)
        implied = contract.implied_volatility(observed_price=price)
        self.assertAlmostEqual(implied, 0.2, places=PLACES)

        contract = BlackScholesPricer(spot=spot,
                                      strike=strike,
                                      discount_curve=self.env.get_curve("curve"),           # noqa
                                      volatility_surface=self.env.get_surface("surface"),   # noqa
                                      valuation_date=self.env.valuation_date,
                                      maturity_date=expiry_date,
                                      convention=self.env.get_constant("daycount"),         # noqa
                                      style=OptionStyle.PUT)
        self.assertEqual(contract.price, 0.8022499147099111)


class TestImpliedVolatilityStatic(unittest.TestCase):
    def setUp(self):
        self.env = Environment()
        self.env.add_constant("daycount",
                              DayCntCnvEnum.basis_act_365_fixed)
        crv = Curve({0.001: 0.0002, 1: 0.0002, 2: 0.0002})
        self.env.add_curve("curve", crv)
        self.env.valuation_date = date(2014, 9, 8)
        self.contract = BlackScholesPricer(spot=586.08,
                                           strike=585,
                                           discount_curve=self.env.get_curve("curve"),      # noqa
                                           volatility_surface=None,
                                           valuation_date=self.env.valuation_date,          # noqa
                                           maturity_date=date(2014, 10, 18),
                                           convention=self.env.get_constant("daycount"),    # noqa
                                           style=OptionStyle.CALL)

    def test_implied_vol(self):
        implied = self.contract.implied_volatility(observed_price=17.5)
        self.assertAlmostEqual(implied, 0.219213836, places=PLACES)


if __name__ == '__main__':
    unittest.main()
