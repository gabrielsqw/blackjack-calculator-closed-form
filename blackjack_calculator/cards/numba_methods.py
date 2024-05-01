import sys
from typing import Literal, Tuple

import numpy as np
from numba import njit

from blackjack_calculator.cards.np import NumpyCards
from blackjack_calculator.house_rules import HouseRules

if sys.version_info >= (3, 11):
    pass
else:
    pass


@njit
def _deck_to_p(deck: np.ndarray):
    d_ = deck.astype(np.float64)
    d_ /= d_.sum()
    return d_


class NumbaCards(NumpyCards):
    """Implement only a subset of methods using numba"""

    @property
    def probabilities(self) -> np.ndarray[Tuple[Literal[11]], np.dtype[np.float64]]:
        return _deck_to_p(self._deck)


if __name__ == "__main__":
    cards = NumbaCards.factory_from_house_rules(HouseRules())
    print(cards.probabilities)
