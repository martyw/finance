from datetime import date, timedelta
import unittest
import utils.date.yearfrac as yf


class TestDaycounts(unittest.TestCase):
    def setUp(self):
        self.start_date = date(2004, 11, 21)
        self.end_date = self.start_date + timedelta(days=181)

    def test_30_360(self):
        dc = yf.DayCountConvention_30_360_isda()
        self.assertEqual(dc.year_fraction(self.start_date, self.end_date),
                         0.5)

    def test_act_365(self):
        dc = yf.DayCountConvention_act_365_fixed()
        self.assertEqual(dc.year_fraction(self.start_date, self.end_date),
                         0.49589041095890413)

    def test_act_act(self):
        dc = yf.DayCountConvention_act_act_isda()
        self.assertEqual(dc.year_fraction(self.start_date, self.end_date),
                         0.49285126132195523)

    def test_factory_function(self):
        start_date = date(2019, 7, 23)
        end_date = date(2020, 7, 23)
        dc = yf.day_count(yf.DayCntCnvEnum.basis_30_360_isda)
        expected = 1
        self.assertEqual(dc.year_fraction(start_date, end_date), expected)
        self.assertEqual(str(dc.convention), "basis_30_360_isda")
