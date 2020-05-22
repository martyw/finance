import unittest
from datetime import date, timedelta
from constants import PLACES
from options.black_scholes import BlackScholesPricer
from options.option_style import OptionStyle
from term_structures.curve import Curve
from term_structures.surface import Surface
from utils.date.yearfrac import DayCntCnvEnum
from utils.parameters.environment import Environment


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
