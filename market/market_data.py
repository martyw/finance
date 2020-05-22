""" A container to store latest known prices for a list of symbols """
import logging
from datetime import datetime
from market.tick_data import TickData


class MarketData:
    def __init__(self):
        self.__recent_ticks__ = dict()

    def add_last_price(self,
                       time: datetime,
                       symbol: str,
                       price: float,
                       volume: int):
        logging.debug("add last {0}, {1} - {2}/{3}".format(time, symbol,
                                                           price, volume))
        tick_data = TickData(symbol=symbol, last_price=price,
                             total_volume=volume, timestamp=time)
        self.__recent_ticks__[symbol] = tick_data

    def add_open_price(self,
                       time: datetime,
                       symbol: str,
                       price: float):
        logging.debug("add open {0}, {1} - {2}".format(time, symbol, price))
        tick_data = self.get_existing_tick_data(symbol)
        tick_data.open_price = price
        self.__recent_ticks__[symbol] = tick_data

    def get_existing_tick_data(self, symbol: str) -> TickData:
        if symbol not in self.__recent_ticks__:
            self.__recent_ticks__[symbol] = TickData(symbol=symbol)

        return self.__recent_ticks__[symbol]

    def get_last_price(self, symbol: str) -> float:
        return self.__recent_ticks__[symbol].last_price

    def get_open_price(self, symbol: str) -> float:
        return self.__recent_ticks__[symbol].open_price

    def get_timestamp(self, symbol: str) -> datetime:
        return self.__recent_ticks__[symbol].timestamp

    def __str__(self):
        return str(self.__recent_ticks__)
