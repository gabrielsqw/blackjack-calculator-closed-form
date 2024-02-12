import sys
from typing import Literal, Tuple

import numpy as np

from blackjack_calculator.cards.abstract import AbstractCards
from blackjack_calculator.house_rules import HouseRules

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


class NumpyCards(
    AbstractCards[np.ndarray[Tuple[Literal[11]], np.dtype[np.int64 | np.float64]]]
):
    @property
    def probabilities(self) -> np.ndarray[Tuple[Literal[11]], np.dtype[np.float64]]:
        d_ = self._deck.astype(float)
        d_ /= d_.sum()
        return d_

    @classmethod
    def factory_from_house_rules(cls, rules: HouseRules) -> Self:
        return cls(
            deck=rules.shoe_size * np.array([0, 4, 4, 4, 4, 4, 4, 4, 4, 4, 16])
        )

    def draw_card(self, card: int) -> Self:
        _arr = np.zeros_like(self._deck)
        _arr[card] += 1
        return type(self)(deck=self._deck - _arr)
