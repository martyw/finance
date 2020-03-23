import unittest

from orderbook.matching_engine import TestExample, TestAlgoSim
from options.black_scholes import TestBSPricer, TestImpliedVolatilityStatic
from term_structures.bootstrap import TestBootstrap
from term_structures.curve import TestCurve
from term_structures.forward_rates import TestForwardCurve
from term_structures.surface import TestSurface
from securities.bond import TestBond
from strategy.mean_reverting import TestMeanReverting
from market.market_data import TestMarketData
from utils.date.yearfrac import TestDaycounts


unittest.main()