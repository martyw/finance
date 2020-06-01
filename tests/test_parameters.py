import unittest
from utils.parameters.environment import Environment


class TestEnvironment(unittest.TestCase):
    def setUp(self) -> None:
        self.env = Environment()

    def test_missing_data(self):
        with self.assertRaises(KeyError):
            self.env.get_curve("Whatever")

    def test_constants(self):
        self.env.add_constant("pi", 3.14)
        self.env.add_constant("pi", 3.14)
        self.assertEqual(self.env.get_constant("pi"), 3.14)


