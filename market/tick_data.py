""" Store a single unit of data """
from datetime import datetime
from dataclasses import dataclass


@dataclass
class TickData:
    symbol: str
    last_price: float = 0.0
    total_volume: int = 0
    timestamp: datetime = datetime.utcnow()


if __name__ == "__main__":
    t = TickData("TEST")
    print(t)
