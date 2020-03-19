"""
side of the order
"""
from enum import IntEnum


class Side(IntEnum):
    """bid or ask"""
    ASK = 1
    BID = -1

    def __str__(self):
        """prints bid or ask"""
        return super().name.lower()
