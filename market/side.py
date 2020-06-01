"""
side of the order
"""
from enum import IntEnum
# pylint: disable=no-member


class Side(IntEnum):
    """bid or ask"""
    ASK = 1
    BID = -1

    def __str__(self) -> str:
        """prints bid or ask"""
        return super().name.lower()
