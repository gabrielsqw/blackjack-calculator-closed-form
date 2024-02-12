import sys
from abc import ABC, abstractmethod
from threading import Lock
from typing import Generic, TypeVar, Tuple, Dict

import pandas as pd

from blackjack_calculator.house_rules import HouseRules

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

_T = TypeVar("_T")


def _default_table() -> pd.DataFrame:
    """returns starting point for hard table so 30-22 for bust cards etc"""
    return pd.DataFrame(
        {i: (
                {"H17": 0, "H18": 0, "H19": 0, "H20": 0, "H21": 0, "BUST": 0} |
                {("BUST" if i > 21 else f"H{i}"): 1}
        ) for i in range(17, 31)}
    )


class AbstractCards(Generic[_T], ABC):
    """for purposes of this repo we assume 10 agnostic"""
    __singleton_cache = {}

    def __new__(cls, deck: _T):
        """use double dunder to indicate cache per concrete class"""
        if not hasattr(cls, "__singleton_cache"):
            cls.__singleton_cache = {}
        with Lock():
            cls_cache = cls.__singleton_cache.get((t := tuple(_T)))
        if cls_cache:
            return cls_cache
        cls_ = super(AbstractCards, cls).__new__(cls, deck=deck)
        with Lock():
            cls.__singleton_cache[t] = cls_
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

        Parameters
        ----------
        dealer_up_card_lbound : int
            lower bound for dealer up card computation
        """
        _hard_cache: Dict[Tuple[str, int]] = {}
        _soft_cache: Dict[Tuple[str, int]] = {}

        _p = self.probabilities
        _p_dict: Dict[int, float] = {i: _p[i] for i in range(1, 11)}

        return pd.DataFrame(_hard_cache), pd.DataFrame(_soft_cache)
