"""
test a strategy with market data from yahoo
keep track of PnL over time
"""
import logging
from datetime import datetime
import pandas as pd

from strategy.mean_reverting import MeanRevertingStrategy
from strategy.market_data_source import MarketDataSource
from strategy.strategy_executor import Executor
from constants import DEFAULT_SERVICE, TEST_MODE


class BackTester(Executor):
    def __init__(self, symbol: str, data_source: str = DEFAULT_SERVICE):
        super().__init__(symbol, data_source)

    def start_back_test(self, start_date: datetime, end_date: datetime, test_mode: bool = False):
        self.strategy = MeanRevertingStrategy(self.symbol, test_mode)

        mds = MarketDataSource(self.symbol, self.market_data_source,
                               start_date, end_date)

        logging.info("Backtesting started...")
        for tick in mds.market_simulation():
            self.market_data_tick(tick)
        logging.info("Completed")


if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s:%(message)s',
                        level=logging.DEBUG)
    back_test = BackTester("AAPL")
    back_test.start_back_test(datetime(2014, 1, 1),
                              datetime(2014, 12, 31), TEST_MODE)

    import matplotlib.pyplot as plt

    dates = [pd.to_datetime(x) for x in back_test.pnl.index.values.tolist()]
    for col in list(back_test.pnl.columns):
        plt.plot(dates, back_test.pnl[col])
    plt.legend(list(back_test.pnl.columns))
    plt.xlabel("time")
    plt.ylabel("Profit and Loss")
    plt.show()
