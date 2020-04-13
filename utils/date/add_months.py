import calendar
import datetime
import unittest


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    return datetime.date(year, month, day)

class TestAddMonths(unittest.TestCase):
    def test_addmonth(self):
        somedate = datetime.date(2019, 11, 9)
        self.assertEqual(add_months(somedate, 1), datetime.date(2019, 12, 9))
        self.assertEqual(add_months(somedate, 2), datetime.date(2020, 1, 9))
        self.assertEqual(add_months(somedate, 5), datetime.date(2020, 4, 9))
        self.assertEqual(add_months(somedate, 23), datetime.date(2021, 10, 9))
        otherdate = datetime.date(2020, 10, 31)
        self.assertEqual(add_months(otherdate, 1), datetime.date(2020, 11, 30))
        anotherdate = datetime.date(2020, 3, 25)
        self.assertEqual(add_months(anotherdate, -1), datetime.date(2020, 2, 25))
        self.assertEqual(add_months(anotherdate, -11), datetime.date(2019, 4, 25))

if __name__ == "__main__":
    unittest.main()
