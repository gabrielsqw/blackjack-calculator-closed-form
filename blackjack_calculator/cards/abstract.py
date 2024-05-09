import sys
from abc import ABC, abstractmethod
from collections import defaultdict
from threading import Lock
from typing import Generic, TypeVar, Tuple

import numpy as np
import pandas as pd

from blackjack_calculator.house_rules import HouseRules

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

_T = TypeVar("_T")


def _default_table(min_num: int = 2) -> pd.DataFrame:
    """returns starting point for hard table so 30-22 for bust cards etc"""
    return pd.DataFrame(
        {
            i: (
                {"H17": 0, "H18": 0, "H19": 0, "H20": 0, "H21": 0, "BUST": 0}
                | ({("BUST" if i > 21 else f"H{i}"): 1} if i >= 17 else {})
            )
            for i in range(min_num, 33)
        }
    )


class AbstractCards(Generic[_T], ABC):
    """for purposes of this repo we assume 10 agnostic"""

    __singleton_cache: dict[type, dict] = defaultdict(dict)

    def __new__(cls, deck: _T):
        """use double dunder to indicate cache per concrete class"""
        with Lock():
            cls_cache = cls.__singleton_cache[cls].get((t := tuple(deck)))
        if cls_cache:
            return cls_cache
        cls_ = super(AbstractCards, cls).__new__(cls)
        with Lock():
            cls.__singleton_cache[cls][t] = cls_
        return cls_

    def __init__(self, deck: _T):
        self._deck = deck

    @property
    @abstractmethod
    def probabilities(self) -> _T:
        """Obtain probabilities for next draw realization, some array of sized 10"""

    @abstractmethod
    def draw_card(self, card: int) -> Self:
        """returns object after drawing a card"""

    @classmethod
    @abstractmethod
    def factory_from_house_rules(cls, rules: HouseRules) -> Self:
        """returns an initial instance of object given house rules"""

    def construct_table(
        self, dealer_up_card_lbound: int = 2
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Constructs a table with rows = dealer outcome and columns = current score
        This table should have no blackjack case; and if there is such, it should be
        extensible from this table. List of such cases: Dealer up card 10 with no peek,
        Dealer up card A. Also +1 special table for dealer up card 10 with peek and no
        Ace

        Currently, this returns pandas dataframes for simplicity. Default implementation
        is done for clarity, this method should be overridden for performance in
        subclasses

        Assumes dealer stands on soft 17, to implement general case later

        Parameters
        ----------
        dealer_up_card_lbound : int
            lower bound for dealer up card computation
        """
        _p: _T = self.probabilities
        _p_np: np.ndarray = np.zeros(11)
        for i in range(1, 11):
            _p_np[i] = _p[i]
        _p_idx = np.arange(11)
        _hard_cache = _default_table(max(dealer_up_card_lbound, 2))
        for i in range(16, 10, -1):
            _hard_cache[i] = (_p_np * _hard_cache[_p_idx + i]).sum(axis=1)
        _soft_cache = _default_table(max(dealer_up_card_lbound, 11))
        _soft_cache[list(range(22, 33))] = _hard_cache[list(range(12, 23))]
        for i in range(16, 10, -1):
            _soft_cache[i] = (_p_np * _soft_cache[_p_idx + i]).sum(axis=1)
        if dealer_up_card_lbound < 11:
            ace_p = _p_np[1]
            _p_np[1] = 0
            for i in range(11, max(dealer_up_card_lbound, 2) - 1, -1):
                _hard_cache[i] = (_p_np * _hard_cache[_p_idx + i]).sum(
                    axis=1
                ) + ace_p * _soft_cache[i + 11]

        return _hard_cache, _soft_cache
