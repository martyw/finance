from datetime import date
from datetime import timedelta
from enum import Enum


class ShiftConvention(Enum):
    NONE = 0
    FOLLOWING = 1
    MODIFIED_FOLLOWING = 2
    PRECEDING = 3
    MODIFIED_PRECEDING = 4


def shift_convention(convention):
    """factory method"""
    if convention == ShiftConvention.NONE:
        retval = DateShiftNone()
    elif convention == ShiftConvention.FOLLOWING:
        retval = Following()
    elif convention == ShiftConvention.MODIFIED_FOLLOWING:
        retval = MofifiedFollowing()
    elif convention == ShiftConvention.PRECEDING:
        retval = Preceding()
    elif convention == ShiftConvention.MODIFIED_FOLLOWING:
        retval = MofifiedPreceding()
    else:
        raise KeyError("Unknown date shift conevention {}".format(convention))

    return retval


class DateShiftNone:
    def __init__(self, convention=ShiftConvention.NONE):
        self.convetion = convention
        self.one_day = timedelta(days=1)

    def shift(self, dt, holidays=[]):
        return dt

    @staticmethod
    def is_business_day(dt: date, holidays=[]):
        if dt.weekday() in (5, 6) or dt in holidays:
            return False
        else:
            return True


class Following(DateShiftNone):
    def __init__(self):
        super().__init__(ShiftConvention.FOLLOWING)

    def shift(self, dt: date, holidays=[]):
        d = super().shift(dt, holidays)
        while not self.is_business_day(d, holidays):
            d += self.one_day

        return d


class MofifiedFollowing(DateShiftNone):
    def __init__(self):
        super().__init__(ShiftConvention.MODIFIED_FOLLOWING)

    def shift(self, dt: date, holidays=[]):
        d = super().shift(dt, holidays)
        while not self.is_business_day(d, holidays):
            d += self.one_day
        if dt.month != d.month:
            d = dt
            while not self.is_business_day(d, holidays):
                d -= self.one_day

        return d


class Preceding(DateShiftNone):
    def __init__(self):
        super().__init__(ShiftConvention.PRECEDING)

    def shift(self, dt: date, holidays=[]):
        d = super().shift(dt, holidays)
        while not self.is_business_day(d, holidays):
            d -= self.one_day

        return d


class MofifiedPreceding(DateShiftNone):
    def __init__(self):
        super().__init__(ShiftConvention.PRECEDING)

    def shift(self, dt: date, holidays=[]):
        d = super().shift(dt, holidays)
        while not self.is_business_day(d, holidays):
            d -= self.one_day
        if dt.month != d.month:
            d = dt
            while not self.is_business_day(d, holidays):
                d += self.one_day

        return d
