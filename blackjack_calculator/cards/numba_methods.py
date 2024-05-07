from typing import Literal, Tuple

import numpy as np
from numba import njit

from blackjack_calculator.cards.np import NumpyCards
from blackjack_calculator.house_rules import HouseRules


@njit
def _deck_to_p(deck: np.ndarray):
    d_ = deck.astype(np.float64)
    d_ /= d_.sum()
    return d_


def _list_default_table() -> list[list[float]]:
    return_list = [[0.0 for _ in range(33)] for _ in range(5)]
    return_list[0][17] = 1.0
    return_list[1][18] = 1.0
    return_list[2][19] = 1.0
    return_list[3][20] = 1.0
    return_list[4][21] = 1.0
    return_list.append([0.0 for _ in range(22)] + [1.0 for _ in range(11)])
    return return_list


_default_table = _list_default_table()


def _numba_default_tables() -> tuple[np.ndarray, np.ndarray]:
    """Returns (hard, soft) tables with links between both tables"""
    hard = np.array(_default_table, dtype=np.float64)
    soft = np.array(_default_table, dtype=np.float64)
    soft[22:33] = hard[12:23]
    return hard, soft


class NumbaCards(NumpyCards):
    """Implement only a subset of methods using numba"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._hard_cache, self._soft_cache = _numba_default_tables()

    @property
    def probabilities(self) -> np.ndarray[Tuple[Literal[11]], np.dtype[np.float64]]:
        return _deck_to_p(self._deck)

    def construct_table_exact_np(
            self, dealer_up_card_lbound: int = 2
    ) -> tuple[np.ndarray, np.ndarray]:
        if dealer_up_card_lbound >= 17:
            return _numba_default_tables()

    def shortcut_odds(self, current_score: int, is_soft: bool) -> np.ndarray:
        table = self._soft_cache if is_soft else self._hard_cache
        if table[:, current_score].any():
            return table[:, current_score]


if __name__ == "__main__":
    cards = NumbaCards.factory_from_house_rules(HouseRules())
    print(cards.probabilities)
    print(_numba_default_tables())
