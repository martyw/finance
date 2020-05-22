from math import exp
import unittest
from term_structures.curve import Curve


class TestCurve(unittest.TestCase):
    """
    Test Curve class
    """
    def setUp(self) -> None:
        self.discount_curve = Curve({0.5: 0.0378,
                                     1.0: 0.0389,
                                     1.5: 0.0401,
                                     2.0: 0.0413,
                                     2.5: 0.0425,
                                     3.0: 0.04375,
                                     3.5: 0.0450})

    def test_discount(self):
        df = [0.9812774850850906, 0.9618468890261952, 0.9416232794985323,
              0.9207193613169226, 0.8991998200185832, 0.876998497358217,
              0.8542768136084795]
        self.assertEqual(self.discount_curve.discount_factors, df)

    def test_string(self):
        string_value = "{0.5: 0.0378, 1.0: 0.0389, 1.5: 0.0401, 2.0: 0.0413, 2.5: 0.0425, 3.0: 0.04375, 3.5: 0.045}"    # noqa
        self.assertEqual(str(self.discount_curve), string_value)

    def test_curve(self):
        """test method"""
        times = range(1, 4)
        factors = [exp(-0.05*t) for t in times]
        crv = Curve(zip(times, factors))
        self.assertEqual(crv.rates, [0.951229424500714,
                                     0.9048374180359595,
                                     0.8607079764250578])
