from enum import IntEnum


class OptionStyle(IntEnum):
    """call or put"""
    PUT = -1
    CALL = 1

    def __str__(self):
        """returns style"""
        return super().name.lower()
