"""Cash flow class plus generator. TODO: extend with date shifts for bank holidays/weekends"""
import unittest
from datetime import date
from typing import List

from utils.date.yearfrac import  DayCntCnvEnum, day_count, DayCountConvention
from utils.date.add_months import add_months
from utils.date.date_shifts import DateShiftNone


class Cashflow:
    def __init__(self,
                 start_date: date,
                 end_date: date,
                 amount: float,
                 daycount: DayCountConvention):
        self._start_date = start_date
        self._end_date = end_date
        self.amount = amount
        self.daycount = daycount


    @property
    def year_fraction(self):
        return self.daycount.year_fraction(self._start_date, self._end_date)

    @property
    def start_date(self):
        return self._start_date

    @start_date.setter
    def start_date(self, val):
        self._start_date = val

    @property
    def end_date(self):
        return self._end_date

    @end_date.setter
    def end_date(self, val):
        self._end_date = val

    def __eq__(self, other):
        return not self.start_date < other.start_date and \
               not other.start_date < self.start_date

    def __ne__(self, other):
        return self.start_date < other.start_date or\
               other.start_date < self.start_date

    def __gt__(self, other):
        return other.start_date < self.start_date

    def __ge__(self, other):
        return not self.start_date < other.start_date

    def __le__(self, other):
        return not other.start_date < self.start_date

    def __repr__(self):
        return "({}/{}, {}, {}/{})".format(self.start_date,
                                           self.end_date,
                                           self.amount,
                                           self.daycount,
                                           self.year_fraction)


class CashFlowSchedule:
    def __init__(self,
                 amount: float,
                 start_date: date,
                 maturity_date: date,
                 frequency: int,
                 daycount: DayCountConvention,
                 date_shift: DateShiftNone,
                 holidays: List[date] = None
                 ):

        self.cashflows = []

        self.amount = amount
        self.start_date = start_date
        self.maturity_date = maturity_date
        self.frequency = frequency
        self.daycount = daycount
        self.date_shift = date_shift
        self.holidays = holidays

    def generate_cashflows(self):
        dt = self.maturity_date
        number_months_in_swaplet = int(12/self.frequency)
        while dt > self.start_date:
            prev = dt
            dt = add_months(dt, -1 * number_months_in_swaplet)
            dt = self.date_shift.shift(dt, self.holidays)
            self.cashflows.append(Cashflow(start_date=dt,
                                           end_date=prev,
                                           amount=self.amount,
                                           daycount=self.daycount
                                           )
                                  )

        self.cashflows = sorted(self.cashflows)

        if self.cashflows and self.cashflows[0].start_date < self.start_date:
            self.cashflows[0].start_date = self.start_date

    def __getitem__(self, item):
        return self.cashflows[item]

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


if __name__ == "__main__":
    unittest.main()
