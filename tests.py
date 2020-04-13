import unittest

from market.market_data import TestMarketData  # noqa
from options.black_scholes import TestBSPricer, TestImpliedVolatilityStatic  # noqa
from orderbook.matching_engine import TestExample, TestAlgoSim  # noqa
from securities.bond import TestBond  # noqa
from securities.swap import TestSwap
from securities.cash_flow_schedule import TestCashFlow
from strategy.mean_reverting import TestMeanReverting  # noqa
from term_structures.bootstrap import TestBootstrap  # noqa
from term_structures.curve import TestCurve  # noqa
from term_structures.forward_rates import TestForwardCurve  # noqa
from term_structures.surface import TestSurface  # noqa
from utils.date.add_months import TestAddMonths  # noqa
from utils.date.yearfrac import TestDaycounts  # noqa
from api.app_server import ApiTest

if __name__ == "__main__":
    unittest.main()
