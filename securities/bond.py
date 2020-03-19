""" Bond class and calculations """
import unittest
from scipy.optimize import newton


class Bond:
    """Attributes needed to price a bond"""
    def __init__(self,
                 par: float,
                 maturity_term: float,
                 coupon: float,
                 price: float = None,
                 ytm: float = None,
                 compounding_frequency: int = 2):

        self.par = par
        self.maturity_term = maturity_term
        self.coupon = coupon / 100.0
        self._price = price
        self._ytm = ytm
        self.compounding_frequency = compounding_frequency

    @property
    def price(self) -> float:
        """return price of this bond, calculate if needed"""
        if self._price is None:
            self._price = self.price_calculator(self.par, self.maturity_term,
                                                self._ytm, self.coupon,
                                                self.compounding_frequency)

        return self._price

    @property
    def yield_to_maturity(self) -> float:
        """return yield-to-maturity of a bond """
        if self._ytm is None:
            self._ytm = self.ytm_calculator(self._price, self.par,
                                            self.maturity_term, self.coupon,
                                            self.compounding_frequency)

        return self._ytm

    @staticmethod
    def ytm_calculator(price: float, par: float, maturity_term: float,
                       coupon: float, compound_freq: int = 2) -> float:
        """ calculate the yield-to-maturity of a bond """
        cpn_freq = float(compound_freq)
        cpn_payment = (coupon * par) / cpn_freq
        num_cpns = int(maturity_term * compound_freq)
        cpn_dates = [(i + 1) / compound_freq for i in range(num_cpns)]

        def ytm_func(y):
            """the equation to solve for ytm"""
            nonlocal cpn_payment, cpn_freq, cpn_dates
            # coupons
            ytm = 0.0
            for t in cpn_dates:
                ytm += cpn_payment / (1 + y / cpn_freq) ** (cpn_freq * t)
            # redemption
            ytm += par / (1 + y / cpn_freq) ** (cpn_freq * maturity_term)
            ytm -= price

            return ytm

        return newton(ytm_func, coupon)

    @staticmethod
    def price_calculator(par: float, maturity_term: float, ytm: float,
                         coupon: float, compound_frequency: int) -> float:
        """ Get bond price from YTM """
        cpn_freq = float(compound_frequency)
        cpn_payment = (coupon * par) / cpn_freq
        num_cpns = int(maturity_term * compound_frequency)
        coupon_dates = [(i + 1) / compound_frequency for i in range(num_cpns)]
        price = 0.0
        for t in coupon_dates:
            price += cpn_payment / (1 + ytm / cpn_freq) ** (cpn_freq * t)
        price += par / (1 + ytm / cpn_freq) ** (cpn_freq * maturity_term)

        return price

    def mod_duration(self, delta_yield=0.01) -> float:
        """ Calculate modified duration """
        (price_minus, price_plus) = self.calc_price_bumps(delta_yield)
        mduration = (price_minus - price_plus) / (2 * self.price * delta_yield)

        return mduration

    def convexity(self, delta_yield=0.01) -> float:
        """ Calculate convexity"""
        (price_minus, price_plus) = self.calc_price_bumps(delta_yield)

        convexity = (price_minus + price_plus - 2 * self.price)
        convexity /= (self.price * delta_yield ** 2)

        return convexity

    def calc_price_bumps(self, delta_yield=0.01) -> (float, float):
        """calculate deltas for duration and convexity calculation"""
        ytm_minus = self.yield_to_maturity - delta_yield
        price_minus = self.price_calculator(self.par,
                                            self.maturity_term,
                                            ytm_minus,
                                            self.coupon,
                                            self.compounding_frequency)

        ytm_plus = self.yield_to_maturity + delta_yield
        price_plus = self.price_calculator(self.par,
                                           self.maturity_term,
                                           ytm_plus,
                                           self.coupon,
                                           self.compounding_frequency)

        return (price_minus, price_plus)


class TestBond(unittest.TestCase):
    """test bond functionality"""

    def setUp(self):
        """initialize the test bonds"""
        self.bond_with_known_price = Bond(100, 1.5, 5.75, 95.0428, None, 2)
        self.bond_with_known_ytm = Bond(100, 1.5, 5.75, None,
                                        0.09369155345239477, 2)
        self.another_bond_with_known_price = Bond(100, 2.5, 5.0,
                                                  95.92, None, 2)
        self.one_more_bond_with_known_price = Bond(100, 10.0, 6.0,
                                                   None, 0.08, 2)

    def test_ytm(self):
        """test yield to maturity calculation"""
        self.assertEqual(0.093691553452,
                         round(self.bond_with_known_price.yield_to_maturity,
                               12))
        self.assertEqual(0.06802229654625709,
                         self.another_bond_with_known_price.yield_to_maturity)

    def test_price(self):
        """test price calculation"""
        self.assertEqual(95.0428, round(self.bond_with_known_ytm.price, 4))

    def test_mduration(self):
        """test modified duration calculation"""
        self.assertEqual(1.392,
                         round(self.bond_with_known_price.mod_duration(), 3))
        self.assertEqual(7.178422566280552,
                         self.one_more_bond_with_known_price.mod_duration())

    def test_convexity(self):
        """test convexity calculation"""
        self.assertEqual(2.6339593903,
                         round(self.bond_with_known_price.convexity(), 10))


if __name__ == '__main__':
    unittest.main()
