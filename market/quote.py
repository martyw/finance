"""
utility class to set proper attributes for Order class
"""
from dataclasses import dataclass


@dataclass
class Quote:
    type: str
    dealer_or_broker_id: str
    side: str
    quantity: int
    price: float = 0.0
    symbol: str = None
