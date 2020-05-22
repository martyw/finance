from datetime import date
import unittest
from term_structures.surface import Surface


class TestSurface(unittest.TestCase):
    def test_curve(self):
        expiries = [date(2006, 2, 11),
                    date(2006, 4, 11),
                    date(2006, 7, 11),
                    date(2006, 10, 11),
                    date(2007, 1, 11),
                    date(2008, 1, 11),
                    date(2009, 1, 11),
                    date(2010, 1, 11),
                    date(2011, 1, 11),
                    date(2012, 1, 11),
                    date(2013, 1, 11)]
        tenors = [0, 1, 2]
        # initialize surface with zeros
        vols = [[0.0 for x in range(len(tenors))]
                for y in range(len(expiries))]
        # expiry, tenor surface                    1y    2y     3y
        vols[0][0],  vols[0][1],  vols[0][2] = 200.00, 76.25, 64.00  # 1m
        vols[1][0],  vols[1][1],  vols[1][2] = 98.50, 84.75, 69.00   # 3m
        vols[2][0],  vols[2][1],  vols[2][2] = 98.00, 81.75, 68.00   # 6m
        vols[3][0],  vols[3][1],  vols[3][2] = 101.25, 82.25, 69.25  # 9m
        vols[4][0],  vols[4][1],  vols[4][2] = 106.00, 82.00, 69.25  # 1y
        vols[5][0],  vols[5][1],  vols[5][2] = 78.75, 73.25, 61.25   # 2y
        vols[6][0],  vols[6][1],  vols[6][2] = 66.25, 59.00, 50.00   # 3y
        vols[7][0],  vols[7][1],  vols[7][2] = 55.25, 47.75, 41.75   # 4y
        vols[8][0],  vols[8][1],  vols[8][2] = 44.75, 40.25, 35.50   # 5y
        vols[9][0],  vols[9][1],  vols[9][2] = 32.00, 30.50, 28.25   # 6y
        vols[10][0], vols[10][1], vols[10][2] = 26.50, 24.25, 24.25  # 7y

        base = date(2006, 1, 11)
        sig = Surface([m for m in tenors],
                      [(t - base).days / 365.0 for t in expiries],
                      vols)
        for i in range(len(expiries)):
            for j in range(len(tenors)):
                expiry = (expiries[i] - base).days/365.0
                vol = sig(float(tenors[j]), expiry)
                self.assertEqual(vol, vols[i][j])
