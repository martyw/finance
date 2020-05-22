from datetime import date
import unittest
from securities.cash_flow_schedule import CashFlowSchedule
from utils.date.date_shifts import DateShiftNone
from utils.date.yearfrac import DayCntCnvEnum, day_count


class TestCashFlow(unittest.TestCase):
    def test_regular_flows(self):
        sl = CashFlowSchedule(amount=100.0,
                              start_date=date(2020, 1, 6),
                              maturity_date=date(2023, 1, 6),
                              frequency=2,
                              daycount=day_count(DayCntCnvEnum.basis_30_360_isda),
                              date_shift=DateShiftNone())
        sl.generate_cashflows()
        self.assertEqual(len(sl.cashflows), 6)
        self.assertEqual(sl[0].start_date, date(2020, 1, 6))
        self.assertEqual(sl[1].start_date, date(2020, 7, 6))
        self.assertEqual(sl[2].start_date, date(2021, 1, 6))
        self.assertEqual(sl[3].start_date, date(2021, 7, 6))
        self.assertEqual(sl[4].start_date, date(2022, 1, 6))
        self.assertEqual(sl[5].start_date, date(2022, 7, 6))

    def test_stub(self):
        sl = CashFlowSchedule(amount=100.0,
                              start_date=date(2020, 4, 6),
                              maturity_date=date(2023, 1, 6),
                              frequency=2,
                              daycount=day_count(DayCntCnvEnum.basis_30_360_isda),
                              date_shift=DateShiftNone())
        sl.generate_cashflows()
        self.assertEqual(len(sl.cashflows), 6)
        self.assertEqual(sl[0].start_date, date(2020, 4, 6))
        self.assertEqual(sl[1].start_date, date(2020, 7, 6))
        self.assertEqual(sl[2].start_date, date(2021, 1, 6))
        self.assertEqual(sl[3].start_date, date(2021, 7, 6))
        self.assertEqual(sl[4].start_date, date(2022, 1, 6))
        self.assertEqual(sl[5].start_date, date(2022, 7, 6))

        self.assertEqual(sl[0].year_fraction, 0.25)
        self.assertEqual(sl[1].year_fraction, 0.5)
        self.assertEqual(sl[2].year_fraction, 0.5)
        self.assertEqual(sl[3].year_fraction, 0.5)
        self.assertEqual(sl[4].year_fraction, 0.5)
        self.assertEqual(sl[5].year_fraction, 0.5)

