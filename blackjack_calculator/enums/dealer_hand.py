from enum import Enum, auto


class DealerHand(Enum):
    """Enum containing states of final dealer hand:
    Hard 17 - 21, blackjack, bust
    so order is BUST < "<=16" < 17 < 18 ... < 21 < BJ
    """
    H17 = auto()
    H18 = auto()
    H19 = auto()
    H20 = auto()
    H21 = auto()
    BJ = auto()
    BUST = auto()
