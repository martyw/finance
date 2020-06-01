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

    def shift(self, this_date, holidays=list()):
        return this_date

    @staticmethod
    def is_business_day(this_date: date, holidays=list()):
        retval = True

        if this_date.weekday() in (5, 6) or this_date in holidays:
            retval = False

        return retval


class Following(DateShiftNone):
    def __init__(self):
        super().__init__(ShiftConvention.FOLLOWING)

    def shift(self, this_date: date, holidays=list()):
        this_date = super().shift(this_date, holidays)
        while not self.is_business_day(this_date, holidays):
            this_date += self.one_day

        return this_date


class MofifiedFollowing(DateShiftNone):
    def __init__(self):
        super().__init__(ShiftConvention.MODIFIED_FOLLOWING)

    def shift(self, this_date: date, holidays=list()):
        tmp_date = super().shift(this_date, holidays)
        while not self.is_business_day(tmp_date, holidays):
            tmp_date += self.one_day
        if this_date.month != tmp_date.month:
            tmp_date = this_date
            while not self.is_business_day(tmp_date, holidays):
                tmp_date -= self.one_day

        return tmp_date


class Preceding(DateShiftNone):
    def __init__(self):
        super().__init__(ShiftConvention.PRECEDING)

    def shift(self, this_date: date, holidays=list()):
        this_date = super().shift(this_date, holidays)
        while not self.is_business_day(this_date, holidays):
            this_date -= self.one_day

        return this_date


class MofifiedPreceding(DateShiftNone):
    def __init__(self):
        super().__init__(ShiftConvention.PRECEDING)

    def shift(self, this_date: date, holidays=list()):
        this_date = super().shift(this_date, holidays)
        while not self.is_business_day(this_date, holidays):
            this_date -= self.one_day
        if this_date.month != this_date.month:
            this_date = this_date
            while not self.is_business_day(this_date, holidays):
                this_date += self.one_day

        return this_date
