from datetime import date
import unittest
from utils.date.date_shifts import DateShiftNone, Following,\
    MofifiedFollowing, Preceding, MofifiedPreceding


class TestDateShifts(unittest.TestCase):
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
        ds = MofifiedPreceding()
        self.assertEqual(ds.shift(dt), date(2019, 6, 28))

    def test_shift_weekday(self):
        dt = date(2019, 7, 23)  # Tuesday
        ds = Following()
        self.assertEqual(ds.shift(dt), date(2019, 7, 23))
        ds = MofifiedFollowing()
        self.assertEqual(ds.shift(dt), date(2019, 7, 23))
        ds = Preceding()
        self.assertEqual(ds.shift(dt), date(2019, 7, 23))
