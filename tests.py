import unittest

from orderbook.matching_engine import TestExample, TestAlgoSim              # noqa
from options.black_scholes import TestBSPricer, TestImpliedVolatilityStatic # noqa
from term_structures.bootstrap import TestBootstrap                         # noqa
from term_structures.curve import TestCurve                                 # noqa
from term_structures.forward_rates import TestForwardCurve                  # noqa
from term_structures.surface import TestSurface                             # noqa
from securities.bond import TestBond                                        # noqa
from strategy.mean_reverting import TestMeanReverting                       # noqa
from market.market_data import TestMarketData                               # noqa
from utils.date.yearfrac import TestDaycounts                               # noqa
from utils.date.add_months import TestAddMonths                              # noqa


unittest.main()
