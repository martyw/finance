from datetime import date
import unittest
from utils.date.add_months import add_months

class TestAddMonths(unittest.TestCase):
    def test_addmonth(self):
        somedate = date(2019, 11, 9)
        self.assertEqual(add_months(somedate, 1), date(2019, 12, 9))
        self.assertEqual(add_months(somedate, 2), date(2020, 1, 9))
        self.assertEqual(add_months(somedate, 5), date(2020, 4, 9))
        self.assertEqual(add_months(somedate, 23), date(2021, 10, 9))
        otherdate = date(2020, 10, 31)
        self.assertEqual(add_months(otherdate, 1), date(2020, 11, 30))
        anotherdate = date(2020, 3, 25)
        self.assertEqual(add_months(anotherdate, -1), date(2020, 2, 25))
        self.assertEqual(add_months(anotherdate, -11), date(2019, 4, 25))
