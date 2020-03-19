"""
for curve construction and calculation
ad a spot_rate attribute to store th calculated zero rate
"""
from securities.bond import Bond


class CurveBond(Bond):
    """instrument to use in yield curve construction"""
    def __init__(self,
                 par: float,
                 maturity_term: float,
                 coupon: float,
                 price: float,
                 compounding_frequency: int = 2):
        super().__init__(par,
                         maturity_term,
                         coupon,
                         price,
                         None,
                         compounding_frequency)
        self._spot_rate = 0.0

    @property
    def spot_rate(self):
        return self._spot_rate

    @spot_rate.setter
    def spot_rate(self, value):
        self._spot_rate = value
