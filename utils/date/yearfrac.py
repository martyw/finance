"""Implements the yearfrac function from Excel
"""
import unittest
from calendar import isleap
from datetime import date, timedelta
from enum import Enum


class DayCntCnvEnum(Enum):
    undefined = -1
    basis_30_360_isda = 0
    basis_act_360 = 1
    basis_act_365_fixed = 2
    basis_act_act_isda = 3

    def __str__(self):
        """prints name"""
        return super().name.lower()


def day_count(convention):
    """factory method"""
    if convention == DayCntCnvEnum.basis_act_360:
        retval = DayCountConvention_act_360()
    elif convention == DayCntCnvEnum.basis_act_365_fixed:
        retval = DayCountConvention_act_365_fixed()
    elif convention == DayCntCnvEnum.basis_act_act_isda:
        retval = DayCountConvention_act_act_isda()
    elif convention == DayCntCnvEnum.basis_30_360_isda:
        retval = DayCountConvention_30_360_isda()
    else:
        raise KeyError("Unknown daycount {}".format(convention))

    return retval


class DayCountConvention:
    def __init__(self, convention=DayCntCnvEnum.undefined):
        self.convetion = convention

    def year_fraction(self, from_date: date, to_date: date):
        assert to_date >= from_date

    def __repr__(self):
        return str(self.convetion)


class DayCountConvention_act_360(DayCountConvention):
    def __init__(self):
        super().__init__(DayCntCnvEnum.basis_act_360)

    def year_fraction(self, from_date: date, to_date: date):
        super().year_fraction(from_date, to_date)
        return (to_date - from_date).days / 360.0


class DayCountConvention_act_365_fixed(DayCountConvention):
    def __init__(self):
        super().__init__(DayCntCnvEnum.basis_act_365_fixed)

    def year_fraction(self, from_date: date, to_date: date):
        super().year_fraction(from_date, to_date)
        return (to_date - from_date).days / 365.0


class DayCountConvention_act_act_isda(DayCountConvention):
    def __init__(self):
        super().__init__(DayCntCnvEnum.basis_act_act_isda)

    def year_fraction(self, from_date: date, to_date: date):
        super().year_fraction(from_date, to_date)
        if from_date.year != to_date.year:
            start_of_to = date(to_date.year, 1, 1)
            end_of_from = date(from_date.year, 12, 31)

            days_in_from_year = 366.0 if isleap(from_date.year) else 365.0
            days_in_to_year = 366.0 if isleap(to_date.year) else 365.0

            retval = (end_of_from - from_date).days / days_in_from_year
            retval += to_date.year - from_date.year - 1
            retval += (to_date - start_of_to).days / days_in_to_year
        else:
            days_in_year = 366.0 if isleap(to_date.year) else 365.0
            retval = (to_date - from_date).days / days_in_year

        return retval


class DayCountConvention_30_360_isda(DayCountConvention):
    def __init__(self):
        super().__init__(DayCntCnvEnum.basis_30_360_isda)

    def year_fraction(self, from_date: date, to_date: date):
        super().year_fraction(from_date, to_date)
        from_day = from_date.day
        if from_day == 31:
            from_day = 30
        to_day = to_date.day
        if to_day == 31:
            to_day = 30

        retval = to_day - from_day
        retval += 30.0 * (to_date.month - from_date.month)
        retval += 360.0 * (to_date.year - from_date.year)
        retval /= 360.0

        return retval


class TestDaycounts(unittest.TestCase):
    def setUp(self):
        self.start_date = date(2004, 11, 21)
        self.end_date = self.start_date + timedelta(days=181)

    def test_30_360(self):
        dc = DayCountConvention_30_360_isda()
        self.assertEqual(dc.year_fraction(self.start_date, self.end_date),
                         0.5)

    def test_act_365(self):
        dc = DayCountConvention_act_365_fixed()
        self.assertEqual(dc.year_fraction(self.start_date, self.end_date),
                         0.49589041095890413)

    def test_act_act(self):
        dc = DayCountConvention_act_act_isda()
        self.assertEqual(dc.year_fraction(self.start_date, self.end_date),
                         0.49285126132195523)

    def test_factory_function(self):
        start_date = date(2019, 7, 23)
        end_date = date(2020, 7, 23)
        dc = day_count(DayCntCnvEnum.basis_30_360_isda)
        expected = 1
        self.assertEqual(dc.year_fraction(start_date, end_date), expected)
        self.assertEqual(str(dc.convetion), "basis_30_360_isda")


if __name__ == '__main__':
    unittest.main()
