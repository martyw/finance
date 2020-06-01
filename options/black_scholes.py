import logging
from datetime import date
from math import log, sqrt, exp

from scipy.stats import norm
from constants import PRECISION, MAX_ITERATIONS
from options.option_style import OptionStyle
from term_structures.curve import Curve
from term_structures.surface import Surface
from utils.date.yearfrac import day_count, DayCntCnvEnum


# pylint: disable=too-many-arguments
# pylint: disable=invalid-name
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
        assert call_put_flag in (-1, 1)
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
        assert call_put_flag in(-1, 1)

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
