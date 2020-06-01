"""Cash flow class plus generator.
TODO: extend with date shifts for bank holidays/weekends
"""
from datetime import date
from typing import List

from utils.date.add_months import add_months
from utils.date.date_shifts import DateShiftNone
from utils.date.yearfrac import DayCountConvention


class CashFlow:
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


# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments
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
        tmp_date = self.maturity_date
        number_months_in_swaplet = int(12/self.frequency)
        while tmp_date > self.start_date:
            prev = tmp_date
            tmp_date = add_months(tmp_date, -1 * number_months_in_swaplet)
            tmp_date = self.date_shift.shift(tmp_date, self.holidays)
            self.cashflows.append(CashFlow(start_date=tmp_date,
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
