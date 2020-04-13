import datetime

import pandas_datareader as web
from requests_cache import CachedSession

from market.market_data import MarketData


class MarketDataSource:
    """ Download prices from an external data source """

    def __init__(self, ticker, source, start, end):
        self.ticker = ticker
        self.source = source
        self.start = start
        self.end = end

    def market_simulation(self):
        expire_after = datetime.timedelta(days=365)
        session = CachedSession(cache_name='cache',
                                backend='sqlite',
                                expire_after=expire_after)

        data = web.DataReader(self.ticker,
                              data_source=self.source,
                              start=self.start,
                              end=self.end,
                              session=session)
        for time, row in data.iterrows():
            md = MarketData()
            md.add_last_price(time, self.ticker, row["Close"], row["Volume"])
            md.add_open_price(time, self.ticker, row["Open"])
            yield md


if __name__ == "__main__":
    import logging

    logging.basicConfig(format='%(levelname)s:%(message)s',
                        level=logging.DEBUG)

    mds = MarketDataSource("AAPL",
                           "yahoo",
                           datetime.datetime(2014, 1, 1),
                           datetime.datetime(2014, 12, 31))
    for i in mds.market_simulation():
        print(i)
