from enum import Enum
from enum import auto


class LongShort(Enum):
    NO_POSITION = auto()
    SHORT = auto()
    LONG = auto()

    def __str__(self):
        """prints long or short"""
        return super().name.lower()
