import unittest
from datetime import timedelta
from datetime import date
from enum import Enum


class ShiftConvention(Enum):
    NONE = 0
    FOLLOWING = 1
    MODIFIED_FOLLOWING = 2
    PRECEDING = 3
    MODIFIED_PRECEDING = 4


class DateShiftNone:
    def __init__(self, convention=ShiftConvention.NONE):
        self.convetion = convention
        self.one_day = timedelta(days=1)

    def shift(self, dt, holidays=[]):
        assert isinstance(dt, date)
        return dt

    @staticmethod
    def is_business_day(dt, holidays=[]):
        assert isinstance(dt, date)
        if dt.weekday() in (5, 6) or dt in holidays:
            return False
        else:
            return True


class Following(DateShiftNone):
    def __init__(self):
        super().__init__(ShiftConvention.FOLLOWING)

    def shift(self, dt, holidays=[]):
        d = super().shift(dt, holidays)
        while not self.is_business_day(d, holidays):
            d += self.one_day

        return d


class MofifiedFollowing(DateShiftNone):
    def __init__(self):
        super().__init__(ShiftConvention.MODIFIED_FOLLOWING)

    def shift(self, dt, holidays=[]):
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

    def shift(self, dt, holidays=[]):
        d = super().shift(dt, holidays)
        while not self.is_business_day(d, holidays):
            d -= self.one_day

        return d


class MofifiedPreceding(DateShiftNone):
    def __init__(self):
        super().__init__(ShiftConvention.PRECEDING)

    def shift(self, dt, holidays=[]):
        d = super().shift(dt, holidays)
        while not self.is_business_day(d, holidays):
            d -= self.one_day
        if dt.month != d.month:
            d = dt
            while not self.is_business_day(d, holidays):
                d += self.one_day

        return d


class TestThis(unittest.TestCase):
    def test_is_business_day(self):
        ds = DateShiftNone()
        dt = date(2019, 7, 23)
        self.assertEqual(ds.is_business_day(dt), True)

        dt = date(2019, 7, 21)
        self.assertEqual(ds.is_business_day(dt), False)

        dt = date(2019, 4, 22)
        holidays = []
        holidays.append(date(2019, 1, 1))
        holidays.append(date(2019, 4, 19))
        holidays.append(date(2019, 4, 21))
        holidays.append(date(2019, 4, 22))
        holidays.append(date(2019, 4, 27))
        holidays.append(date(2019, 5, 5,))
        holidays.append(date(2019, 5, 30))
        holidays.append(date(2019, 6, 9))
        holidays.append(date(2019, 6, 10))
        holidays.append(date(2019, 12, 25))
        holidays.append(date(2019, 12, 26))
        self.assertEqual(ds.is_business_day(dt, holidays), False)

        dt = date(2019, 4, 27)  # Bank holiday on a Saturday
        self.assertEqual(ds.is_business_day(dt, holidays), False)

        dt = date(2019, 7, 23)  # Tuesday
        self.assertEqual(ds.is_business_day(dt, holidays), True)

    def test_shift_weekend(self):
        dt = date(2019, 6, 30)  # Sunday
        ds = Following()
        self.assertEqual(ds.shift(dt), date(2019, 7, 1))
        ds = MofifiedFollowing()
        self.assertEqual(ds.shift(dt), date(2019, 6, 28))
        ds = Preceding()
        self.assertEqual(ds.shift(dt), date(2019, 6, 28))

    def test_shift_weekday(self):
        dt = date(2019, 7, 23)  # Tuesday
        ds = Following()
        self.assertEqual(ds.shift(dt), date(2019, 7, 23))
        ds = MofifiedFollowing()
        self.assertEqual(ds.shift(dt), date(2019, 7, 23))
        ds = Preceding()
        self.assertEqual(ds.shift(dt), date(2019, 7, 23))


if __name__ == '__main__':
    unittest.main()
