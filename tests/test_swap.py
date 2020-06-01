from datetime import date
import unittest
from securities.swap import FixedSwapLeg, FloatingSwapLeg, Swap
from term_structures.curve import Curve
from utils.date.yearfrac import DayCntCnvEnum
from utils.date.date_shifts import ShiftConvention
from utils.parameters.environment import Environment


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

        daycount = self.env.get_constant("fixed_daycount_code")
        dateshift = self.env.get_constant("fixed_dateshift_convention")
        fixed_leg = FixedSwapLeg(principal_amount=100000000,
                                 start_date=date(2020, 1, 6),
                                 maturity_date=date(2023, 1, 6),
                                 frequency=2,
                                 daycount_code=daycount,
                                 dateshift_code=dateshift,
                                 discount_curve=self.env.get_curve("discount"),
                                 valuation_date=self.env.valuation_date,
                                 holidays=self.env.get_constant("holidays")
                                 )
        daycount = self.env.get_constant("float_daycount_code")
        dateshift = self.env.get_constant("float_dateshift_convention")
        discount = self.env.get_curve("discount")
        forward = self.env.get_curve("forward")
        holidays = self.env.get_constant("holidays")
        floating_leg = FloatingSwapLeg(principal_amount=100000000,
                                       start_date=date(2020, 1, 6),
                                       maturity_date=date(2023, 1, 6),
                                       frequency=2,
                                       daycount_code=daycount,
                                       dateshift_code=dateshift,
                                       discount_curve=discount,
                                       forward_curve=forward,
                                       valuation_date=self.env.valuation_date,
                                       holidays=holidays
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
