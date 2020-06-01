from datetime import date
from os import linesep
from typing import List

from securities.cash_flow_schedule import CashFlowSchedule, CashFlow
from term_structures.curve import Curve
from term_structures.forward_rates import ForwardRates
from utils.date.date_shifts import ShiftConvention, shift_convention
from utils.date.yearfrac import DayCntCnvEnum, day_count


# pylint: disable=too-many-arguments
class Swaplet(CashFlow):
    def __init__(self,
                 start_date: date,
                 end_date: date,
                 amount: float,
                 daycount,
                 discount_curve: Curve,
                 valuation_date: date = date.today()):
        super().__init__(start_date=start_date, end_date=end_date,
                         amount=amount, daycount=daycount)
        self.discount_curve = discount_curve
        self.valuation_date = valuation_date

    @property
    def discount_factor(self) -> float:
        term = self.daycount.year_fraction(self.valuation_date, self.end_date)
        rate = self.discount_curve.loglinear_interpolate(term)

        return Curve.discount_factor(term, rate)


class FloatingSwaplet(Swaplet):
    def __init__(self,
                 start_date: date,
                 end_date: date,
                 amount: float,
                 daycount,
                 forward_curve: Curve,
                 discount_curve: Curve,
                 valuation_date: date = date.today()
                 ):
        super().__init__(start_date=start_date,
                         end_date=end_date,
                         amount=amount,
                         daycount=daycount,
                         discount_curve=discount_curve,
                         valuation_date=valuation_date)
        self.forward_curve = forward_curve

    @property
    def discounted_amount(self) -> float:
        if self.valuation_date < self.end_date:
            if self.valuation_date <= self.start_date:
                discounted_amount = self.amount * \
                                    self.forward_rate * \
                                    self.discount_factor * \
                                    self.year_fraction
            else:
                raise NotImplementedError("todo")
        else:
            raise NotImplementedError("todo")

        return discounted_amount

    @property
    def forward_rate(self) -> float:
        term1 = self.daycount.year_fraction(self.valuation_date,
                                            self.start_date)
        term2 = self.daycount.year_fraction(self.valuation_date,
                                            self.end_date)
        rate1 = self.forward_curve.loglinear_interpolate(term1)
        rate2 = self.forward_curve.loglinear_interpolate(term2)

        return ForwardRates.forward(term1, rate1, term2, rate2)

    def __repr__(self):
        return "({}/{} amount: {}/discounted: {}, forward rate: {}" \
               "/discount factor:{})".format(self.start_date,
                                             self.end_date,
                                             self.amount,
                                             self.discounted_amount,
                                             self.forward_rate,
                                             self.discount_factor)


class FixedRateSwaplet(Swaplet):
    def __init__(self,
                 start_date: date,
                 end_date: date,
                 amount: float,
                 daycount,
                 discount_curve: Curve,
                 valuation_date: date,
                 fixed_rate: float = 1.0):

        super().__init__(start_date=start_date,
                         end_date=end_date,
                         amount=amount,
                         daycount=daycount,
                         discount_curve=discount_curve,
                         valuation_date=valuation_date)
        self.fixed_rate = fixed_rate
        self.valuation_date = valuation_date

    @property
    def discounted_amount(self) -> float:
        if self.valuation_date < self.end_date:
            if self.valuation_date <= self.start_date:
                discounted_amount = self.fixed_rate * \
                                    self.amount * \
                                    self.discount_factor * \
                                    self.year_fraction
            else:
                raise NotImplementedError("todo")
        else:
            raise NotImplementedError("todo")

        return discounted_amount

    def __repr__(self):
        return "({}/{} amount: {}/discounted: {}, discount factor:{})" \
            .format(self.start_date, self.end_date, self.amount,
                    self.discounted_amount, self.discount_factor)


class FloatingSwapLeg(CashFlowSchedule):
    def __init__(self,
                 principal_amount: float,
                 start_date: date,
                 maturity_date: date,
                 frequency: int,
                 daycount_code: DayCntCnvEnum,
                 dateshift_code: ShiftConvention,
                 discount_curve: Curve,
                 forward_curve: Curve,
                 valuation_date: date = date.today(),
                 holidays: List[date] = None
                 ):

        daycount = day_count(daycount_code)
        dateshift = shift_convention(dateshift_code)

        super().__init__(start_date=start_date,
                         maturity_date=maturity_date,
                         daycount=daycount,
                         amount=principal_amount,
                         frequency=frequency,
                         date_shift=dateshift,
                         holidays=holidays
                         )

        self.generate_cashflows()
        self.swaplets: List[FixedRateSwaplet] = []
        self.forward_curve = forward_curve
        self.discount_curve = discount_curve
        self.valuation_date = valuation_date
        self.holidays = holidays

    @property
    def present_value(self) -> float:
        net_present_value = 0.0
        for cshflw in self.cashflows:
            swplt = FloatingSwaplet(start_date=cshflw.start_date,
                                    end_date=cshflw.end_date,
                                    amount=cshflw.amount,
                                    daycount=self.daycount,
                                    forward_curve=self.forward_curve,
                                    discount_curve=self.discount_curve,
                                    valuation_date=self.valuation_date
                                    )
            self.swaplets.append(swplt)
            net_present_value += swplt.discounted_amount

        return net_present_value

    def __repr__(self):
        rep = ""
        for swplt in self.swaplets:
            rep += format(str(swplt)) + linesep
        return rep


class FixedSwapLeg(CashFlowSchedule):
    def __init__(self,
                 principal_amount: float,
                 start_date: date,
                 maturity_date: date,
                 frequency: int,
                 daycount_code: DayCntCnvEnum,
                 dateshift_code: ShiftConvention,
                 discount_curve: Curve,
                 valuation_date: date = date.today(),
                 holidays: List[date] = None,
                 fixed_rate: float = 1.0):

        self.daycount = day_count(daycount_code)
        dateshift = shift_convention(dateshift_code)

        super().__init__(start_date=start_date,
                         maturity_date=maturity_date,
                         daycount=self.daycount,
                         amount=principal_amount,
                         frequency=frequency,
                         date_shift=dateshift,
                         holidays=holidays
                         )
        self.generate_cashflows()
        self.swaplets: List[FixedRateSwaplet] = []
        self.fixed_rate = fixed_rate
        self.discount_curve = discount_curve
        self.valuation_date = valuation_date
        self.holidays = holidays

    @property
    def present_value(self) -> float:
        self.swaplets = []
        net_present_value = 0.0
        for cshflw in self.cashflows:
            swplt = FixedRateSwaplet(start_date=cshflw.start_date,
                                     end_date=cshflw.end_date,
                                     amount=cshflw.amount,
                                     daycount=self.daycount,
                                     discount_curve=self.discount_curve,
                                     valuation_date=self.valuation_date,
                                     fixed_rate=self.fixed_rate
                                     )
            self.swaplets.append(swplt)
            net_present_value += swplt.discounted_amount

        return net_present_value

    @property
    def fixed_rate(self) -> float:
        return self._fixed_rate

    @fixed_rate.setter
    def fixed_rate(self, val) -> None:
        self._fixed_rate = val

    def __repr__(self):
        rep = ""
        for swplt in self.swaplets:
            rep += format(str(swplt)) + linesep
        return rep


class Swap:
    def __init__(self,
                 fixed_leg: FixedSwapLeg,
                 floating_leg: FloatingSwapLeg,
                 fixed_rate: float = 1.0):
        self.floating_leg = floating_leg
        self.fixed_leg = fixed_leg
        self.fixed_rate: float = fixed_rate

    @property
    def fixed_rate(self) -> float:
        return self._fixed_rate

    @fixed_rate.setter
    def fixed_rate(self, val) -> None:
        self._fixed_rate = val
        self.fixed_leg.fixed_rate = val

    @property
    def fair_rate(self) -> float:
        fixed_leg = self.fixed_leg

        return self.floating_leg.present_value / fixed_leg.present_value

    @property
    def present_value(self) -> float:
        return self.floating_leg.present_value - self.fixed_leg.present_value
