"""Implements the yearfrac function from Excel
"""
from calendar import isleap
from datetime import date
from enum import Enum


# pylint: disable=too-few-public-methods
# pylint: disable=no-self-use
# pylint: disable=invalid-name
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
        self.convention = convention

    def year_fraction(self, from_date: date, to_date: date):
        assert to_date >= from_date

    def __repr__(self):
        return str(self.convention)


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
