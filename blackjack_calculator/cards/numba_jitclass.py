import sys
from typing import Literal, Tuple

import numpy as np
from numba import int32
from numba.experimental import jitclass

from blackjack_calculator.house_rules import HouseRules

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

spec = [
    ("_deck", int32[:])
]


@jitclass(spec)
class NumbaJitclassCards:
    """Attempt jitclass implementation"""

    def __init__(self, deck: np.ndarray):
        self._deck = deck.astype(np.int32)

    @property
    def probabilities(self) -> np.ndarray[Tuple[Literal[11]], np.dtype[np.float64]]:
        d_ = self._deck.astype(np.float64)
        d_ /= d_.sum()
        return d_

    def draw_card(self, card: int) -> Self:
        _arr = np.zeros_like(self._deck)
        _arr[card] += 1
        return NumbaJitclassCards(deck=self._deck - _arr)


if __name__ == "__main__":
    d = HouseRules().shoe_size * np.array([0, 4, 4, 4, 4, 4, 4, 4, 4, 4, 16])
    cards = NumbaJitclassCards(deck=d)
    print(cards.probabilities)
    cards_2 = cards.draw_card(2)
    print(cards_2.probabilities)
