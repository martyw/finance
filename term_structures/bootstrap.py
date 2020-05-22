""" Bootstrapping the yield curve """
from math import log, exp
from typing import List

from securities.bond import Bond
from term_structures.curve import Curve


class BootstrappedCurve(Curve):
    """
    Bootstrap a curve of bond instruments to zero coupon rates
    """
    def __init__(self):
        self._instruments = {}  # Map each maturity to an instrument
        super().__init__({})

    def add_instrument(self, bond):
        """ Save instrument info by maturity """
        self._curve[bond.maturity_term] = None
        self._instruments[bond.maturity_term] = bond

    @property
    def rates(self) -> List:
        """ Calculate list of available zero rates """
        for bond in self._instruments.values():
            if bond.maturity_term not in self._curve:
                raise KeyError("term {} not found in curve".format(bond.maturity_term))
            self._curve[bond.maturity_term] = self.bond_spot_rate(bond)

        return [self._curve[t] for t in self.times]

    def bond_spot_rate(self, bond: Bond) -> float:
        """ return the spot rate for the input bond """
        if bond.coupon == 0:
            # get rate of a zero coupon bond
            spot_rate = log(bond.par / bond.price) / bond.maturity_term
        else:
            # calculate spot rate of a bond
            number_of_periods = \
                int(bond.maturity_term * bond.compounding_frequency)
            value = bond.price
            cpn_payment = bond.coupon * bond.par / bond.compounding_frequency

            for i in range(1, number_of_periods):
                term = i / float(bond.compounding_frequency)
                rate = self._curve[term]
                discounted_coupon_value = cpn_payment * exp(-rate * term)
                value -= discounted_coupon_value

            last = number_of_periods / float(bond.compounding_frequency)
            spot_rate = -log(value / (bond.par + cpn_payment)) / last

        return spot_rate
