from datetime import date
from typing import List
from os import linesep
import unittest

from securities.cash_flow_schedule import CashFlowSchedule, Cashflow
from utils.date.yearfrac import DayCntCnvEnum, day_count
from utils.date.date_shifts import ShiftConvention, shift_convention
from term_structures.curve import Curve
from term_structures.forward_rates import ForwardRates
from utils.parameters.environment import Environment


class Swaplet(Cashflow):
    def __init__(self,
                 start_date: date,
                 end_date: date,
                 amount: float,
                 daycount,
                 discount_curve: Curve,
                 valuation_date: date = date.today()):

        super().__init__(start_date=start_date, end_date=end_date, amount=amount, daycount=daycount)
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
                         valuation_date=valuation_date
                         )
        self.forward_curve=forward_curve

    @property
    def discounted_amount(self) -> float:
        if self.valuation_date < self.end_date:
            if self.valuation_date <= self.start_date:
                discounted_amount = self.amount * self.forward_rate * \
                                         self.discount_factor * self.year_fraction
            else:
                raise NotImplementedError("todo")
        else:
            raise NotImplementedError("todo")

        return discounted_amount

    @property
    def forward_rate(self) -> float:
        term1 = self.daycount.year_fraction(self.valuation_date, self.start_date)
        term2 = self.daycount.year_fraction(self.valuation_date, self.end_date)
        rate1 = self.forward_curve.loglinear_interpolate(term1)
        rate2 = self.forward_curve.loglinear_interpolate(term2)

        return ForwardRates.forward(term1, rate1, term2, rate2)

    def __repr__(self):
        return "({}/{} amount: {}/discounted: {}, forward rate: {}/discount factor:{})".format(self.start_date,
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
        return "({}/{} amount: {}/discounted: {}, discount factor:{})".format(self.start_date,
                                            self.end_date,
                                            self.amount,
                                            self.discounted_amount,
                                            self.discount_factor)

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
        self.swaplets:List[FixedRateSwaplet] = []
        self.forward_curve = forward_curve
        self.discount_curve = discount_curve
        self.valuation_date = valuation_date
        self.holidays = holidays

    @property
    def present_value(self) -> float:
        net_present_value = 0.0
        for cf in self.cashflows:
            swplt = FloatingSwaplet(start_date=cf.start_date,
                                    end_date=cf.end_date,
                                    amount=cf.amount,
                                    daycount = self.daycount,
                                    forward_curve=self.forward_curve,
                                    discount_curve = self.discount_curve,
                                    valuation_date = self.valuation_date
                                    )
            self.swaplets.append(swplt)
            net_present_value += swplt.discounted_amount

        return net_present_value

    def __repr__(self):
        rep = ""
        for swplt in self.swaplets:
            rep+=format(str(swplt))+linesep
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
        self.swaplets:List[FixedRateSwaplet] = []
        self.fixed_rate = fixed_rate
        self.discount_curve = discount_curve
        self.valuation_date = valuation_date
        self.holidays = holidays

    @property
    def present_value(self) -> float:
        self.swaplets = []
        net_present_value = 0.0
        for cf in self.cashflows:
            swplt = FixedRateSwaplet(start_date=cf.start_date,
                                     end_date=cf.end_date,
                                     amount=cf.amount,
                                     daycount=self.daycount,
                                     discount_curve=self.discount_curve,
                                     valuation_date= self.valuation_date,
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
            rep+=format(str(swplt))+linesep
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
        fixed_calculate_leg = self.fixed_leg

        return self.floating_leg.present_value/fixed_calculate_leg.present_value

    @property
    def present_value(self) -> float:
        return self.floating_leg.present_value - self.fixed_leg.present_value

class TestSwap(unittest.TestCase):
    def setUp(self) -> None:
        curve = Curve({0.002777777777777778: 0.038, 0.5: 0.04, 1.0: 0.0411,
                       1.5: 0.0425, 2.0: 0.043, 2.5: 0.045, 3.0: 0.047})

        self.env = Environment()
        self.env.add_constant("fixed_daycount_code", DayCntCnvEnum.basis_30_360_isda)           # noqa
        self.env.add_constant("float_daycount_code", DayCntCnvEnum.basis_30_360_isda)     # noqa
        self.env.add_constant("fixed_dateshift_convention", ShiftConvention.NONE)               # noqa
        self.env.add_constant("float_dateshift_convention", ShiftConvention.NONE)               # noqa
        self.env.add_constant("holidays", [date(2020, 1, 1),
                                           date(2020, 4, 13),
                                           date(2020, 4, 27),
                                           date(2020, 5, 5),
                                           date(2020, 5, 21),
                                           date(2020, 6, 1),
                                           date(2020, 12, 25),
                                           date(2020, 12, 26),
                                           date(2021, 1, 1),
                                           date(2021, 4, 5),
                                           date(2021, 4, 27),
                                           date(2021, 5, 13),
                                           date(2021, 5, 24),
                                           date(2022, 4, 17),
                                           date(2022, 4, 27),
                                           date(2022, 5, 26),
                                           date(2022, 6, 6),
                                           date(2022, 12, 26)
                                           ])
        self.env.add_curve("discount", curve)
        self.env.add_curve("forward", curve)
        self.env.valuation_date = date(2020, 1, 6)

        fixed_leg = FixedSwapLeg(principal_amount=100000000,
                                 start_date=date(2020, 1, 6),
                                 maturity_date=date(2023, 1, 6),
                                 frequency=2,
                                 daycount_code=self.env.get_constant("fixed_daycount_code"),
                                 dateshift_code=self.env.get_constant("fixed_dateshift_convention"),
                                 discount_curve=self.env.get_curve("discount"),
                                 valuation_date=self.env.valuation_date,
                                 holidays=self.env.get_constant("holidays")
                                 )


        floating_leg = FloatingSwapLeg(principal_amount=100000000,
                                       start_date=date(2020, 1, 6),
                                       maturity_date=date(2023, 1, 6),
                                       frequency=2,
                                       daycount_code=self.env.get_constant("float_daycount_code"),
                                       dateshift_code=self.env.get_constant("float_dateshift_convention"),
                                       discount_curve=self.env.get_curve("discount"),
                                       forward_curve=self.env.get_curve("forward"),
                                       valuation_date=self.env.valuation_date,
                                       holidays=self.env.get_constant("holidays")
                                       )

        self.swap = Swap(fixed_leg=fixed_leg, floating_leg=floating_leg)

    def test_swap(self):
        self.assertEqual(self.swap.fair_rate, 0.046764184911059506)
        self.swap.fixed_rate = self.swap.fair_rate
        self.assertEqual(self.swap.present_value, 0.)

    def test_fixed_leg(self):
        self.swap.fixed_rate = self.swap.fair_rate
        self.assertEqual(self.swap.present_value, 0.)
        self.assertEqual(str(self.swap.fixed_leg.swaplets[0]), "(2020-01-06/2020-07-06 amount: 100000000/discounted: 2291909.6004046155, discount factor:0.9801986733067553)")  # noqa
        self.assertEqual(str(self.swap.fixed_leg.swaplets[1]), "(2020-07-06/2021-01-06 amount: 100000000/discounted: 2244056.9288814645, discount factor:0.9597331518337898)")  # noqa
        self.assertEqual(str(self.swap.fixed_leg.swaplets[2]), "(2021-01-06/2021-07-06 amount: 100000000/discounted: 2193800.343813071, discount factor:0.9382395300957113)")   # noqa
        self.assertEqual(str(self.swap.fixed_leg.swaplets[3]), "(2021-07-06/2022-01-06 amount: 100000000/discounted: 2145527.3151050317, discount factor:0.917594231220151)")   # noqa
        self.assertEqual(str(self.swap.fixed_leg.swaplets[4]), "(2022-01-06/2022-07-06 amount: 100000000/discounted: 2089417.5788107426, discount factor:0.8935973471085157)")  # noqa
        self.assertEqual(str(self.swap.fixed_leg.swaplets[5]), "(2022-07-06/2023-01-06 amount: 100000000/discounted: 2030709.7382754267, discount factor:0.8684893116976679)")  # noqa

    def test_floating_leg(self):
        self.swap.fixed_rate = self.swap.fair_rate
        self.assertEqual(self.swap.present_value, 0.)
        self.assertEqual(str(self.swap.floating_leg.swaplets[0]), "(2020-01-06/2020-07-06 amount: 100000000/discounted: 1960397.346613511, forward rate: 0.04000000000000001/discount factor:0.9801986733067553)")  # noqa
        self.assertEqual(str(self.swap.floating_leg.swaplets[1]), "(2020-07-06/2021-01-06 amount: 100000000/discounted: 2025036.9503692966, forward rate: 0.0422/discount factor:0.9597331518337898)")              # noqa
        self.assertEqual(str(self.swap.floating_leg.swaplets[2]), "(2021-01-06/2021-07-06 amount: 100000000/discounted: 2125112.5356667857, forward rate: 0.04529999999999999/discount factor:0.9382395300957113)") # noqa
        self.assertEqual(str(self.swap.floating_leg.swaplets[3]), "(2021-07-06/2022-01-06 amount: 100000000/discounted: 2041647.164464834, forward rate: 0.044499999999999956/discount factor:0.917594231220151)")  # noqa
        self.assertEqual(str(self.swap.floating_leg.swaplets[4]), "(2022-01-06/2022-07-06 amount: 100000000/discounted: 2368032.96983757, forward rate: 0.053000000000000075/discount factor:0.8935973471085157)")  # noqa
        self.assertEqual(str(self.swap.floating_leg.swaplets[5]), "(2022-07-06/2023-01-06 amount: 100000000/discounted: 2475194.538338353, forward rate: 0.056999999999999995/discount factor:0.8684893116976679)") # noqa


if __name__ == "__main__":
    unittest.main()