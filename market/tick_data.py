""" Store a single unit of data """
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TickData:
    symbol: str
    last_price: float = 0.0
    open_price: float = 0.0
    total_volume: int = 0
    timestamp: datetime = datetime.utcnow()
